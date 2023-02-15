#!/bin/bash

set -e

git clone https://github.com/bitdust-io/public.git bitdust_repo
cd bitdust_repo
git pull
git rev-list --count HEAD >../revnum
cd ..

echo "core version is:"
cat core_version
REVNUM=`cat revnum`
echo "revision number based on total amount of commits in the Git repository is"
cat revnum
echo "current version:"
cat version
echo ""
echo "bump version number"
python3 -c "cv=open('core_version').read().strip().split('.');v=list(open('version').read().strip().split('.'));v[0]=cv[0];v[-2]=str(int(v[-2])+1);v[-1]=open('revnum').read().strip();open('version','w').write(('.'.join(v)).strip())"
rm -rf revnum
echo "new version is:"
cat version
echo ""

rm -rf app
mkdir -p app
cp -r ../../../src/* app/
mkdir -p app/bitdust_copy
cd bitdust_repo
git checkout-index -a -f --prefix="../app/bitdust_copy/"
cd ..
mv app/bitdust_copy/bitdust app/
mv app/bitdust_copy/bitdust_forks app/
mv app/bitdust_copy/default_network.json app/
rm -rf app/bitdust/icons
rm -rf app/deploy
rm -rf app/bitdust/devops
rm -rf app/bitdust/regress
rm -rf app/bitdust/regression
rm -rf app/bitdust/tests
rm -rf app/bitdust/icons
rm -rf app/bitdust_copy/

VERSION=`cat version`
echo "__version__ = \"$VERSION\"" > ./app/version.py

make build_android_environment

