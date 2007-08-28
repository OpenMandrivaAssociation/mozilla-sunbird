%define name mozilla-sunbird
%define oname  lightning-sunbird
%define version 0.5
%define release %mkrel 1

%define section Office/Time Management
%define title	Mozilla-Sunbird
%define Summary A standalone calendar application based on Mozilla

#warning: always end release date with 00
# (it should be the hour of build but it is not significant for rpm)
%define date 2005120300

# even if I force mozilla-sunbird-%{version} as libname, make install
# put it in sunbird-0.3a1
%define vers 0.5
%define libname sunbird-%{vers}

%define mozillalibdir %{_libdir}/%{libname}

Summary: %{Summary}
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{oname}-%version-source.tar.bz2
Source1: sunbird-rebuild-databases.pl.in.generatechrome.bz2
Source2: sunbird-generate-chrome.sh.bz2

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
BuildRequires:	ImageMagick 
BuildRequires:  freetype2-devel
BuildRequires:  X11-devel
BuildRequires:	nss-devel
BuildRequires:	nspr-devel
# do not provides mozilla lib
%define _provides_exceptions libgtkembedmoz.so\\|libxp.*
%define _requires_exceptions libgtkembedmoz.so\\|libxp.*

%description
The Sunbird Project is a redesign of the Mozilla Calendar component. 
It aims to produce a cross platform standalone calendar application based on 
Mozilla's XUL user interface language. At the moment the Sunbird name is a 
project name. It is not official and may change in the future.

%package devel
Summary:        Mozilla-sunbird development files
Group:          Development/Other
Requires:       %{name} = %{version}
Conflicts:	%mklibname -d js 1

%description devel
Mozilla-sunbird development files


%prep
%setup -q -c %{name}-%{version}
%setup -T -D -n %{name}-%{version}/mozilla

# let jars get compressed
%__perl -p -i -e 's|\-0|\-9|g' config/make-jars.pl

%build

%define __libtoolize /bin/true
%define __cputoolize /bin/true

export MOZ_SUNBIRD=1
export MOZ_BUILD_DATE=%{date}

%configure \
	--enable-application=calendar --disable-debug --enable-xprint \
	--enable-strip-libs --disable-mathml --with-system-zlib --enable-toolkit=gtk2 \
	--enable-default-toolkit=gtk2 --disable-tests --disable-freetype2 \
	--enable-optimize="$RPM_OPT_FLAGS" --with-default-mozilla-five-home=%{mozillalibdir} \
	--enable-single-profile --disable-profilesharing --disable-ldap --disable-mailnews \
	--enable-extensions=pref,xmlextras --enable-crypto --disable-composer \
	--enable-plaintext-editor-only --enable-necko-protocols=about,http,ftp,file,res \
	--disable-accessibility --disable-activex --disable-activex-scripting --disable-installer \
	--disable-jsd --disable-mathml --disable-necko-disk-cache --disable-oji --disable-view-source \
	--disable-logging --disable-plugins --disable-cookies --enable-application=calendar \
	--enable-xft --disable-pango --with-system-nspr --with-system-nss

%make

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall_std

# multiarch files
%multiarch_binaries $RPM_BUILD_ROOT%{_bindir}/sunbird-config
%multiarch_includes $RPM_BUILD_ROOT%{_includedir}/%{libname}/mozilla-config.h
%multiarch_includes $RPM_BUILD_ROOT%{_includedir}/%{libname}/js/jsautocfg.h

# XDG menu entry
mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Name=%name
Comment=The Sunbird Project is a redesign of the Calendar component
Exec=%{_bindir}/sunbird
Icon=%{name}
Terminal=false
Type=Application
Categories=GNOME;GTK;Office;Calendar;
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
%{_bindir}/sunbird
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



%files devel
%defattr(-,root,root)
%{_libdir}/pkgconfig/*.pc
%{_bindir}/sunbird-config
%multiarch %{multiarch_bindir}/sunbird-config
%{_datadir}/aclocal/*.m4
%{_datadir}/idl/%{libname}
%{_includedir}/%{libname}
%multiarch %{multiarch_includedir}/* 
