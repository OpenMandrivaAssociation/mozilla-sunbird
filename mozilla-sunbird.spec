%define name mozilla-sunbird
%define oname  lightning-sunbird
%define version 0.9
%define release %mkrel 4

%define section Office/Time Management
%define title	Mozilla-Sunbird
%define Summary A standalone calendar application based on Mozilla

#warning: always end release date with 00
# (it should be the hour of build but it is not significant for rpm)
%define date 2007083000

# even if I force mozilla-sunbird-%{version} as libname, make install
# put it in sunbird-0.3a1
%define progname sunbird
%define libname %{progname}-%{version}

%define mozillalibdir %{_libdir}/%{libname}
%define progdir %{mozillalibdir}


Summary: %{Summary}
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{oname}-%version-source.tar.bz2
Source1: sunbird-rebuild-databases.pl.in.generatechrome.bz2
Source2: sunbird-generate-chrome.sh.bz2
Patch0:  sunbird-0.9-fix-str-fmt.patch
Patch1:  nss-opt.patch
Patch2:  abuild.patch
Patch3:  locale.patch
Patch4:  sunbird-0.7-uilocale.patch
Patch5:  mozilla-sunbird-0.8-glibc28-max_path-fix.patch
Patch6:  sunbird-0.9-gcc-4.4.patch
License: MPL/LGPL/GPL
Group: Office
Url: http://www.mozilla.org/projects/calendar
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires:  jpeg-devel
BuildRequires:  png-devel
BuildRequires:  libIDL-devel
BuildRequires:  zip tcsh
BuildRequires:  gtk+2-devel >= 2.2.0
BuildRequires:  gnome-vfs2-devel
BuildRequires:	imagemagick
BuildRequires:  freetype2-devel
BuildRequires:  X11-devel
BuildRequires:	nss-devel
BuildRequires:  libnss-static-devel
BuildRequires:	nspr-devel

# do not provides mozilla lib
%define _provides_exceptions libgtkembedmoz.so\\|libxp.*
%define _requires_exceptions libgtkembedmoz.so\\|libxp.*

%description
The Sunbird Project is a redesign of the Mozilla Calendar component.
It aims to produce a cross platform standalone calendar application based on
Mozilla's XUL user interface language. At the moment the Sunbird name is a
project name. It is not official and may change in the future.

%if 0
%package devel
Summary:        Mozilla-sunbird development files
Group:          Development/Other
Requires:       %{name} = %{version}
Conflicts:	%mklibname -d js 1

%description devel
Mozilla-sunbird development files
%endif

%prep
%setup -q -n mozilla
%patch0 -p1 -b .str
%patch1 -p0 -b .nss
%patch2 -p1 -b .abuild
%patch3 -p0 -b .locale
%patch4 -p1 -b .uilocale
%patch5 -p1 -b .glibc28-max_path-fix
%patch6 -p1 -b .gcc44

# let jars get compressed
%__perl -p -i -e 's|\-0|\-9|g' config/make-jars.pl

%build

%define __libtoolize /bin/true
%define __cputoolize /bin/true

export MOZ_SUNBIRD=1
export MOZ_BUILD_DATE=%{date}
export MOZILLA_OFFICIAL=1
export BUILD_OFFICIAL=1
export CFLAGS="$RPM_OPT_FLAGS -Os -fno-strict-aliasing -fstack-protector"
export CXXFLAGS="$CFLAGS"
export MOZCONFIG=$RPM_BUILD_DIR/mozconfig
cat << EOF > $MOZCONFIG
mk_add_options MOZILLA_OFFICIAL=1
mk_add_options BUILD_OFFICIAL=1
mk_add_options MOZ_MAKE_FLAGS=%{?jobs:-j%jobs}
. \$topsrcdir/calendar/sunbird/config/mozconfig
ac_add_options --prefix=%{_prefix}
ac_add_options --libdir=%{_libdir}
ac_add_options --sysconfdir=%{_sysconfdir}
ac_add_options --mandir=%{_mandir}
ac_add_options --includedir=%{_includedir}
ac_add_options --enable-optimize="$CFLAGS"
ac_add_options --with-system-jpeg
ac_add_options --with-system-png
ac_add_options --with-system-zlib
ac_add_options --enable-default-toolkit=gtk2
ac_add_options --enable-xft
ac_add_options --disable-tests
ac_add_options --disable-freetype2
ac_add_options --disable-installer
ac_add_options --enable-static
ac_add_options --disable-shared
ac_add_options --enable-logging
ac_add_options --enable-official-branding
#ac_add_options --enable-debug
ac_add_options --with-system-nspr
ac_add_options --enable-system-cairo
ac_add_options --with-system-nss
EOF

make -f client.mk build


%install

rm -rf $RPM_BUILD_ROOT
make -C xpinstall/packager STRIP=/bin/true
# copy tree into RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{progdir}
cp -rf $RPM_BUILD_DIR/mozilla/dist/%{progname}/* $RPM_BUILD_ROOT%{progdir}
mkdir $RPM_BUILD_ROOT%{_bindir}
ln -sf ../..%{progdir}/%{progname} $RPM_BUILD_ROOT%{_bindir}/%{progname}

%if 0
# multiarch files
%multiarch_binaries $RPM_BUILD_ROOT%{_bindir}/sunbird-config
%multiarch_includes $RPM_BUILD_ROOT%{_includedir}/%{libname}/mozilla-config.h
%multiarch_includes $RPM_BUILD_ROOT%{_includedir}/%{libname}/js/jsautocfg.h
%endif

# XDG menu entry
mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Name=Mozilla Sunbird
Comment=The Sunbird Project is a redesign of the Calendar component
Exec=%{_bindir}/sunbird
Icon=%{name}
Terminal=false
Type=Application
Categories=GNOME;GTK;Office;Calendar;
StartupWMClass=Sunbird-bin
EOF

install -m 755 -d $RPM_BUILD_ROOT%{_miconsdir}
install -m 755 -d $RPM_BUILD_ROOT%{_iconsdir}
install -m 755 -d $RPM_BUILD_ROOT%{_liconsdir}
convert -resize 16x16  $RPM_BUILD_ROOT%{mozillalibdir}/icons/mozicon50.xpm $RPM_BUILD_ROOT%{_miconsdir}/%{name}.png
convert -resize 32x32  $RPM_BUILD_ROOT%{mozillalibdir}/icons/mozicon50.xpm $RPM_BUILD_ROOT%{_iconsdir}/%{name}.png
convert -resize 48x48  $RPM_BUILD_ROOT%{mozillalibdir}/icons/mozicon50.xpm $RPM_BUILD_ROOT%{_liconsdir}/%{name}.png

# install our rebuild file
bzcat %{SOURCE1} | sed -e "s|mozilla-MOZILLA_VERSION|%{libname}|g;s|LIBDIR|%{_libdir}|g" > \
  $RPM_BUILD_ROOT%{mozillalibdir}/mozilla-rebuild-databases.pl
chmod 755 $RPM_BUILD_ROOT%{mozillalibdir}/mozilla-rebuild-databases.pl

# install our file to rebuild the chrome registry so that we can
# produce nvu extentions in RPM
mkdir -p $RPM_BUILD_ROOT%{mozillalibdir}/chrome/rc.d
bzcat %{SOURCE2} > \
  $RPM_BUILD_ROOT%{mozillalibdir}/chrome/rc.d/generate-chrome.sh

chmod 755 $RPM_BUILD_ROOT%{mozillalibdir}/chrome/rc.d/generate-chrome.sh

# ghost files
mkdir -p $RPM_BUILD_ROOT%{mozillalibdir}/extensions
touch $RPM_BUILD_ROOT%{mozillalibdir}/chrome/chrome.rdf
for overlay in {"browser","communicator","editor","inspector","messenger","navigator"}; do
  %{__mkdir_p} $RPM_BUILD_ROOT%{mozillalibdir}/chrome/overlayinfo/$overlay/content
  touch $RPM_BUILD_ROOT%{mozillalibdir}/chrome/overlayinfo/$overlay/content/overlays.rdf
done
touch $RPM_BUILD_ROOT%{mozillalibdir}/extensions/installed-extensions-processed.txt
touch $RPM_BUILD_ROOT%{mozillalibdir}/extensions/Extensions.rdf
touch $RPM_BUILD_ROOT%{mozillalibdir}/components.ini
touch $RPM_BUILD_ROOT%{mozillalibdir}/defaults.ini
touch $RPM_BUILD_ROOT%{mozillalibdir}/components/compreg.dat
touch $RPM_BUILD_ROOT%{mozillalibdir}/components/xpti.dat
touch $RPM_BUILD_ROOT%{mozillalibdir}/chrome/app-chrome.manifest

# dummy manifest file to avoid chrome registration error in sunbird extension
touch $RPM_BUILD_ROOT%{mozillalibdir}/extensions/{e2fda1a4-762b-4020-b5ad-a41df1933103}/chrome.manifest

%clean
rm -rf $RPM_BUILD_ROOT

%post
export HOME="/root" MOZ_DISABLE_GNOME=1
umask 022

%{_bindir}/sunbird -register
%{mozillalibdir}/mozilla-rebuild-databases.pl

%files
%defattr(-,root,root)
%doc LICENSE LEGAL README.txt
%{_bindir}/%{progname}
%{_datadir}/applications/mandriva-%{name}.desktop
%{_miconsdir}/%{name}.png
%{_iconsdir}/%{name}.png
%{_liconsdir}/%{name}.png
%{mozillalibdir}
%ghost %{mozillalibdir}/chrome/chrome.rdf
%ghost %{mozillalibdir}/chrome/app-chrome.manifest
%ghost %{mozillalibdir}/chrome/overlayinfo/browser/content/overlays.rdf
%ghost %{mozillalibdir}/chrome/overlayinfo/communicator/content/overlays.rdf
%ghost %{mozillalibdir}/chrome/overlayinfo/inspector/content/overlays.rdf
%ghost %{mozillalibdir}/chrome/overlayinfo/messenger/content/overlays.rdf
%ghost %{mozillalibdir}/chrome/overlayinfo/navigator/content/overlays.rdf
%ghost %{mozillalibdir}/extensions/Extensions.rdf
%ghost %{mozillalibdir}/extensions/installed-extensions-processed.txt
%ghost %{mozillalibdir}/components.ini
%ghost %{mozillalibdir}/defaults.ini
%ghost %{mozillalibdir}/components/compreg.dat
%ghost %{mozillalibdir}/components/xpti.dat


%if 0
%files devel
%defattr(-,root,root)
%{_libdir}/pkgconfig/*.pc
%{_bindir}/sunbird-config
%multiarch %{multiarch_bindir}/sunbird-config
%{_datadir}/aclocal/*.m4
%{_datadir}/idl/%{libname}
%{_includedir}/%{libname}
%multiarch %{multiarch_includedir}/*
%endif
