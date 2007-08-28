%define gcj_support 1

Name:		megamek
Version:	0.30.11
Release:	%mkrel 1.2
Epoch:		0
Summary:	A portable, network-enabled BattleTech engine

Group:		Development/Java
License:	GPL
URL:		http://megamek.sourceforge.net/
Source0:	http://ovh.dl.sourceforge.net/megamek/MegaMek-v0.30.11.tar.bz2
# converted from data/images/misc/megamek-icon.gif
Source1:	megamek-icon.png
Patch0:		megamek-directories.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root

BuildRequires:		desktop-file-utils
BuildRequires:		ImageMagick
%if %{gcj_support}
BuildRequires:		java-gcj-compat-devel
%else
BuildRequires:		java-devel
BuildArch:		noarch
%endif
BuildRequires:		jpackage-utils
Requires(post):		desktop-file-utils
Requires(postun):	desktop-file-utils
%if %{gcj_support}
Requires(post):		java-gcj-compat
Requires(postun):	java-gcj-compat
%endif
Requires:		jpackage-utils
Provides:		MegaMek = %{epoch}:%{version}-%{release}

%description
MegaMek is a community effort to implement the Classic BattleTech
rules in an operating-system-agnostic, network-enabled manner.

%prep
%setup -q -c -n MegaMek
%patch0 -p0
# remove included binaries and rebuild everything from source
rm -f MegaMek.exe MegaMek.jar
rm -f lib/TinyXML.jar lib/retroweaver-rt.jar
pushd src
  %{jar} xf ../lib/Ostermiller.jar
  # remove hard-to-build sources that are not required
  rm -f com/Ostermiller/util/*CSV*
  rm -f com/Ostermiller/util/*CGI*
  rm -f com/Ostermiller/util/*Properties*
  rm -r com/Ostermiller/util/*Browser*
  rm -rf META-INF
  %{jar} xf ../lib/PngEncoder.jar
  rm -rf META-INF
  rm -f LICENSE.txt PngEncoderB.html PngEncoder.html
  %{jar} xf ../lib/TabPanel.jar
  rm -rf META-INF gov doc
  rm -f LICENSE README
  mv src/gov .
  rmdir src
  unzip -qq ../lib/tinyXML07-src.zip
  mv sources/*.java .
  mv sources/gd .
  rm -rf classes javadoc
  rmdir sources
  rm -f DevelopmentDiary-TinyXML.txt readme.txt gpl.txt
  %{jar} xf ../lib/collections.jar
  rm -rf META-INF
  rm -f ../lib/collections.jar
  find -name \*.class | xargs rm -f
  rm -f ../lib/Ostermiller.jar ../lib/PngEncoder.jar
  rm -f ../lib/TabPanel.jar ../lib/tinyXML07-src.zip
  find -name .svn | xargs rm -rf
  cp ../l10n/megamek/client/*.properties megamek/client
  cp ../l10n/megamek/client/bot/*.properties megamek/client/bot
  cp ../l10n/megamek/common/*.properties megamek/common
  cp ../l10n/megamek/common/options/*.properties megamek/common/options
popd
find data docs mmconf -name .svn -print0 | xargs -0 rm -rf
find data docs mmconf -type f -print0 | xargs -0 chmod 644
find data docs mmconf -type d -print0 | xargs -0 chmod 755
rm -f mmconf/MegaMek.bat
mv docs/stats.pl .

%build
pushd src
  %{javac} `find -name '*.java'`
  %{jar} cf megamek.jar com gd gnu gov keypoint megamek *.class *.java
popd

cat > megamek.sh << EOF
#!/bin/sh
#
# megamek script
# JPackage Project <http://www.jpackage.org/>
# $Id$

# Source functions library
. /usr/share/java-utils/java-functions

# Source system prefs
if [ -f /etc/megamek.conf ] ; then
  . /etc/megamek.conf
fi

# Source user prefs
if [ -f $HOME/.megamekrc ] ; then
  . $HOME/.megamekrc
fi

# Configuration
MAIN_CLASS=megamek.MegaMek
BASE_DIR=/usr/share/megamek

# Set parameters
set_jvm
CLASSPATH=$(build-classpath megamek)
set_flags $BASE_FLAGS
set_options $BASE_OPTIONS

# Let's start
run "$@"
EOF

cat > megamek.desktop << EOF
[Desktop Entry]
Name=MegaMek
GenericName=A BattleTech engine
Comment=Play MegaMek
Exec=megamek
Icon=megamek-icon.png
Terminal=false
Type=Application
Categories=Game;BoardGame;
Version=%{version}
EOF

%install
rm -rf $RPM_BUILD_ROOT

install -dm 755 $RPM_BUILD_ROOT%{_javadir}
install -pm 644 src/megamek.jar \
  $RPM_BUILD_ROOT%{_javadir}/megamek.jar

install -dm 755 $RPM_BUILD_ROOT%{_datadir}/megamek
cp -r data docs mmconf $RPM_BUILD_ROOT%{_datadir}/megamek
install -pm 644 readme.txt \
  $RPM_BUILD_ROOT%{_datadir}/megamek/readme.txt

install -dm 755 $RPM_BUILD_ROOT%{_bindir}
install -pm 755 megamek.sh \
  $RPM_BUILD_ROOT%{_bindir}/megamek
install -pm 755 stats.pl \
  $RPM_BUILD_ROOT%{_bindir}/megamek-stats

install -dm 755 $RPM_BUILD_ROOT%{_datadir}/applications
desktop-file-install --vendor "" \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications \
  --remove-category Application \
  --add-category X-MandrivaLinux-MoreApplications-Games-Arcade \
  megamek.desktop

install -dm 755 $RPM_BUILD_ROOT%{_datadir}/pixmaps
install -pm 644 %{SOURCE1} \
  $RPM_BUILD_ROOT%{_datadir}/pixmaps/megamek.png

%{__mkdir_p} %{buildroot}%{_datadir}/icons/hicolor/16x16/apps
%{__mkdir_p} %{buildroot}%{_datadir}/icons/hicolor/24x24/apps
%{__mkdir_p} %{buildroot}%{_datadir}/icons/hicolor/32x32/apps
%{_bindir}/convert -resize 16x16 %{SOURCE1} %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
%{_bindir}/convert -resize 24x24 %{SOURCE1} %{buildroot}%{_datadir}/icons/hicolor/24x24/apps/%{name}.png
%{__cp} -a %{SOURCE1} %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/%{name}.png

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{gcj_support}
%post
%{update_gcjdb}
%endif
%{update_desktop_database}
%update_icon_cache hicolor

%postun
%if %{gcj_support}
%{clean_gcjdb}
%endif
%{clean_desktop_database}
%clean_icon_cache hicolor

%files
%defattr(-,root,root,-)
%doc HACKING license.txt readme-German.txt readme.txt
%{_javadir}/megamek.jar
%{_datadir}/megamek
%{_bindir}/megamek
%{_bindir}/megamek-stats
%{_datadir}/applications/megamek.desktop
%{_datadir}/pixmaps/%{name}.png
%{_datadir}/icons/hicolor/16x16/apps/%%{name}.png
%{_datadir}/icons/hicolor/24x24/apps/%%{name}.png
%{_datadir}/icons/hicolor/32x32/apps/%%{name}.png
%if %{gcj_support}
%dir %attr(-,root,root) %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/megamek.jar.*
%endif


