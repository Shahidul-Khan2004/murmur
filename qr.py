from __future__ import annotations
from io import BytesIO
from pathlib import Path

import qrcode
from qrcode.constants import (
	ERROR_CORRECT_H,
	ERROR_CORRECT_L,
	ERROR_CORRECT_M,
	ERROR_CORRECT_Q,
)

from PIL import Image, ImageOps


def generate_qr_code_from_text(
	text: str,
	*,
	max_words: int = 250,
	error_correction: str = "Q",
	box_size: int = 10,
	border: int = 0,
) -> bytes:
	"""Generate a QR code PNG (as bytes) from text.

	Parameters
	----------
	text:
		The text content to encode.

	This function does not write to disk; it returns the PNG bytes so other
	functions can store, transmit, or further process the QR code.
	max_words:
		Safety limit for word count. Defaults to 250.
	error_correction:
		One of "L", "M", "Q", "H". Lower is higher capacity.
	box_size:
		Pixel size of each QR module.
	border:
		Border size (in modules).

	Returns
	-------
	bytes
		PNG-encoded QR code image.
	"""

	if not isinstance(text, str) or not text.strip():
		raise ValueError("text must be a non-empty string")

	word_count = len(text.split())
	if word_count > max_words:
		raise ValueError(
			f"text has {word_count} words; maximum allowed is {max_words}"
		)

	error_correction_map = {
		"L": ERROR_CORRECT_L,
		"M": ERROR_CORRECT_M,
		"Q": ERROR_CORRECT_Q,
		"H": ERROR_CORRECT_H,
	}
	error_correction = error_correction.upper().strip()
	if error_correction not in error_correction_map:
		raise ValueError('error_correction must be one of "L", "M", "Q", "H"')

	qr = qrcode.QRCode(
		version=None,
		error_correction=error_correction_map[error_correction],
		box_size=box_size,
		border=border,
	)

	try:
		qr.add_data(text)
		qr.make(fit=True)
		img = qr.make_image(fill_color="black", back_color="white")
	except Exception as exc:  # pragma: no cover
		raise ValueError(
			"Text could not be encoded into a QR code with the given settings. "
			"Try using a lower error correction level (e.g. 'L') or shortening the text."
		) from exc

	buf = BytesIO()
	img.save(buf, format="PNG")
	return buf.getvalue()


def merge_qr_into_image(
	qr_png: bytes,
	image: str | Path | bytes,
	*,
	position: str = "bottom-right",
	qr_scale: float = 0.02,
	margin_px: int = 16,
	quiet_zone_px: int = 2,
	qr_opacity: float = 0.32,
	plate_opacity: float = 0.20,
	min_qr_px: int = 96,
	output_format: str = "PNG",
	jpeg_quality: int = 90,
) -> bytes:
	"""Blend a QR code into an image (subtle but scannable) and return bytes.

	Parameters
	----------
	qr_png:
		QR code image as PNG bytes.
	image:
		Base image as a path or raw bytes.
	position:
		"br", "bl", "tr", "tl", "center", or full names like "bottom-right".
	qr_scale:
		QR size as a fraction of the smaller base dimension.
	margin_px:
		Inset from image edges.
	quiet_zone_px:
		Extra white padding around the QR (in pixels) to help scanning.
	qr_opacity:
		Opacity for the black QR modules (0..1). Lower hides more, scans less.
	plate_opacity:
		Opacity for a subtle white plate behind the QR (0..1).
	min_qr_px:
		Minimum QR width/height in pixels.
	output_format:
		"PNG" or "JPEG".
	jpeg_quality:
		JPEG quality if output_format is "JPEG".

	Returns
	-------
	bytes
		Merged image bytes.
	"""

	if not isinstance(qr_png, (bytes, bytearray)) or len(qr_png) == 0:
		raise ValueError("qr_png must be non-empty bytes")

	if isinstance(image, (str, Path)):
		base = Image.open(image)
	elif isinstance(image, (bytes, bytearray)):
		base = Image.open(BytesIO(image))
	else:
		raise TypeError("image must be a path or bytes")

	base = base.convert("RGBA")
	base_w, base_h = base.size

	qr_img = Image.open(BytesIO(qr_png)).convert("RGBA")

	# Make a crisp black/white representation of the QR.
	lum = qr_img.convert("L")
	bw = lum.point(lambda p: 255 if p > 128 else 0, mode="L")

	# Determine QR target size within the base image.
	available = max(1, min(base_w, base_h) - 2 * margin_px)
	target = int(min(base_w, base_h) * qr_scale)
	target = max(target, min_qr_px)
	target = min(target, available)

	# Preserve module crispness.
	try:
		nearest = Image.Resampling.NEAREST
	except AttributeError:  # pragma: no cover
		nearest = Image.NEAREST

	bw = bw.resize((target, target), resample=nearest)

	# Add a quiet zone around the QR.
	if quiet_zone_px > 0:
		bw = ImageOps.expand(bw, border=int(quiet_zone_px), fill=255)

	qw, qh = bw.size
	if qw + 2 * margin_px > base_w or qh + 2 * margin_px > base_h:
		scale = min(
			(base_w - 2 * margin_px) / max(1, qw),
			(base_h - 2 * margin_px) / max(1, qh),
		)
		new_size = (max(1, int(qw * scale)), max(1, int(qh * scale)))
		bw = bw.resize(new_size, resample=nearest)
		qw, qh = bw.size

	# Mask for black modules.
	black_mask = bw.point(lambda p: 255 if p < 128 else 0, mode="L")

	# Build overlay: a subtle white plate + semi-opaque black modules.
	overlay = Image.new("RGBA", (qw, qh), (0, 0, 0, 0))
	if plate_opacity > 0:
		plate_alpha = max(0, min(255, int(255 * plate_opacity)))
		plate = Image.new("RGBA", (qw, qh), (255, 255, 255, plate_alpha))
		overlay.alpha_composite(plate)

	if qr_opacity > 0:
		qr_alpha = max(0, min(255, int(255 * qr_opacity)))
		black_layer = Image.new("RGBA", (qw, qh), (0, 0, 0, qr_alpha))
		overlay.paste(black_layer, (0, 0), mask=black_mask)

	pos = position.lower().strip().replace("_", "-")
	pos_map = {
		"br": "bottom-right",
		"bottom-right": "bottom-right",
		"bottomright": "bottom-right",
		"bl": "bottom-left",
		"bottom-left": "bottom-left",
		"bottomleft": "bottom-left",
		"tr": "top-right",
		"top-right": "top-right",
		"topright": "top-right",
		"tl": "top-left",
		"top-left": "top-left",
		"topleft": "top-left",
		"center": "center",
	}
	pos = pos_map.get(pos)
	if pos == "bottom-right":
		x, y = base_w - qw - margin_px, base_h - qh - margin_px
	elif pos == "bottom-left":
		x, y = margin_px, base_h - qh - margin_px
	elif pos == "top-right":
		x, y = base_w - qw - margin_px, margin_px
	elif pos == "top-left":
		x, y = margin_px, margin_px
	elif pos == "center":
		x, y = (base_w - qw) // 2, (base_h - qh) // 2
	else:
		raise ValueError(
			'position must be one of "br", "bl", "tr", "tl", "center" '
			'or "bottom-right", "bottom-left", "top-right", "top-left"'
		)

	out = base.copy()
	out.alpha_composite(overlay, (x, y))

	fmt = output_format.upper().strip()
	buf = BytesIO()
	if fmt in ("JPG", "JPEG"):
		out.convert("RGB").save(buf, format="JPEG", quality=jpeg_quality, optimize=True)
	else:
		out.save(buf, format="PNG")
	return buf.getvalue()

