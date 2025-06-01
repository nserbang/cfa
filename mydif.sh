
#!/bin/bash
# place new directory in cfa direcoryr and execute this from cfa_server directory
# Usage check
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <new_dir> <cfa_server_dir>"
  exit 1
fi

new_dir="$1"
cfa_dir="$2"

diff -rq "$new_dir" "$cfa_dir" \
  | grep -E '^Files .*\.((py)|(html)|(js)|(css)) .* differ$' \
  | grep -vE 'api/migrations|/migrations/|cfa_server/test' \
  | awk '{print $2}' > diffs

echo "Diff file list saved to 'diffs'"

