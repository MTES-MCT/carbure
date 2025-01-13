cd build
latest_index=$(ls index.*.html | head -n 1)
ln -sf "$latest_index" index.html