#!/bin/sh

ROOT_DIR=/usr/share/nginx/html

for file in $ROOT_DIR/assets/*.js $ROOT_DIR/index.html;
do
  sed -i 's|https://data-copilot.azurefd.net|'${VITE_API_URL}'|g' $file
done

echo "done"
nginx -g 'daemon off;'