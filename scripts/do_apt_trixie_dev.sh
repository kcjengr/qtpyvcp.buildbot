#!/usr/bin/env bash

# Scan for new debian packages in apt repository

cd /home/buildbot/debian/apt

dpkg-scanpackages --arch amd64 pool/main/trixie-dev > dists/trixie-dev/main/binary-amd64/Packages
cat dists/trixie-dev/main/binary-amd64/Packages | gzip -9 > dists/trixie-dev/main/binary-amd64/Packages.gz

dpkg-scanpackages --arch arm64 pool/main/trixie-dev > dists/trixie-dev/main/binary-arm64/Packages
cat dists/trixie-dev/main/binary-arm64/Packages | gzip -9 > dists/trixie-dev/main/binary-arm64/Packages.gz


cd /home/buildbot/debian/apt/dists/trixie-dev

/home/buildbot/debian/generate-trixie-dev.sh > Release

export GPG_TTY=$(tty)
export GNUPGHOME="/home/buildbot/debian/pgpkeys"

cat /home/buildbot/debian/apt/dists/trixie-dev/Release | gpg --default-key 2DEC041F290DF85A -abs > /home/buildbot/debian/apt/dists/trixie-dev/Release.gpg
cat /home/buildbot/debian/apt/dists/trixie-dev/Release | gpg --default-key 2DEC041F290DF85A -abs --clearsign > /home/buildbot/debian/apt/dists/trixie-dev/InRelease

