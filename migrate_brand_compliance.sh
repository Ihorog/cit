#!/bin/bash
# CIMEIKA Brand Compliance Migration Script
# Auto-generated - Review before executing!

set -e

echo '📁 Renaming folders...'
find . -depth -type d -name 'podija' -exec bash -c 'mv "$0" "${0%podija}podiya"' {} \;
find . -depth -type d -name 'nastrij' -exec bash -c 'mv "$0" "${0%nastrij}nastriy"' {} \;
find . -depth -type d -name 'gallery' -path '*/modules/*' -exec bash -c 'mv "$0" "${0%gallery}galereya"' {} \;
find . -depth -type d -name 'calendar' -path '*/modules/*' -exec bash -c 'mv "$0" "${0%calendar}kalendar"' {} \;

echo '📝 Updating file contents...'
find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.jsx' -o -name '*.sql' \) \
  -exec sed -i 's|modules/podija|modules/podiya|g' {} +
find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.jsx' -o -name '*.sql' \) \
  -exec sed -i 's|modules/nastrij|modules/nastriy|g' {} +
find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.jsx' -o -name '*.sql' \) \
  -exec sed -i 's|modules/gallery|modules/galereya|g' {} +
find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.jsx' -o -name '*.sql' \) \
  -exec sed -i 's|modules/calendar|modules/kalendar|g' {} +
find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.jsx' -o -name '*.sql' \) \
  -exec sed -i 's|/podija/|/podiya/|g' {} +
find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.jsx' -o -name '*.sql' \) \
  -exec sed -i 's|/nastrij/|/nastriy/|g' {} +
find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.jsx' -o -name '*.sql' \) \
  -exec sed -i 's|/gallery/|/galereya/|g' {} +
find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.jsx' -o -name '*.sql' \) \
  -exec sed -i 's|/calendar/|/kalendar/|g' {} +
find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.jsx' -o -name '*.sql' \) \
  -exec sed -i 's|'podija'|'podiya'|g' {} +
find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.jsx' -o -name '*.sql' \) \
  -exec sed -i 's|'nastrij'|'nastriy'|g' {} +
find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.jsx' -o -name '*.sql' \) \
  -exec sed -i 's|'gallery'|'galereya'|g' {} +
find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.jsx' -o -name '*.sql' \) \
  -exec sed -i 's|'calendar'|'kalendar'|g' {} +

echo '✅ Migration complete!'
echo '⚠️ Please review changes and run tests before committing'
