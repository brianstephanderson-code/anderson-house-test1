#!/usr/bin/env bash
set -euo pipefail

# Pinned reference implementation / bundled sherpa-onnx Android runtime.
# Source: https://github.com/suddenBook/GPTWake (Apache-2.0)
REV="2e31652be39b1751a6a75eac3027716b7d5286b1"
BASE="https://raw.githubusercontent.com/suddenBook/GPTWake/$REV/app"

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)/app"
LIB_DIR="$APP_DIR/libs"
JNI_DIR="$APP_DIR/src/main/jniLibs/arm64-v8a"
KWS_DIR="$APP_DIR/src/main/assets/kws"

mkdir -p "$LIB_DIR" "$JNI_DIR" "$KWS_DIR"

get() {
  local rel="$1"
  local out="$2"
  if [ -s "$out" ]; then
    return 0
  fi
  echo "Fetching $rel"
  curl -fL --retry 3 --retry-delay 2 "$BASE/$rel" -o "$out"
}

get "libs/sherpa-onnx-1.13.4-classes.jar" "$LIB_DIR/sherpa-onnx-1.13.4-classes.jar"

for f in \
  libonnxruntime.so \
  libsherpa-onnx-c-api.so \
  libsherpa-onnx-cxx-api.so \
  libsherpa-onnx-jni.so
do
  get "src/main/jniLibs/arm64-v8a/$f" "$JNI_DIR/$f"
done

for f in \
  encoder-epoch-13-avg-2-chunk-16-left-64.int8.onnx \
  decoder-epoch-13-avg-2-chunk-16-left-64.onnx \
  joiner-epoch-13-avg-2-chunk-16-left-64.int8.onnx \
  tokens.txt \
  empty_keywords.txt
do
  get "src/main/assets/kws/$f" "$KWS_DIR/$f"
done

echo "Hey Tomo wake dependencies ready."
