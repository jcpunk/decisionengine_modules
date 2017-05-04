#%define version __DECISIONENGINE_RPM_VERSION__
#%define release __DECISIONENGINE_RPM_RELEASE__
%define version 0.1
%define release 0.1

%define de_user decisionengine
%define de_group decisionengine

%define de_confdir %{_sysconfdir}/decisionengine
%define de_channel_confdir %{_sysconfdir}/decisionengine/config.d
%define de_logdir %{_localstatedir}/log/decisionengine
%define de_lockdir %{_localstatedir}/lock/decisionengine
%define systemddir %{_prefix}/lib/systemd/system

%define le_builddir %{_builddir}/decisionengine/framework/logicengine/cxx/build

# From http://fedoraproject.org/wiki/Packaging:Python
# Define python_sitelib
%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%define de_python_sitelib $RPM_BUILD_ROOT%{python_sitelib}

Name:           decisionengine
Version:        %{version}
Release:        %{release}
Summary:        The HEPCloud Decision Engine Framework

Group:          System Environment/Daemons
License:        Fermitools Software Legal Information (Modified BSD License)
URL:            http://hepcloud.fnal.gov

Source0:        decisionengine.tar.gz
#Source1:        ../../../framework/logicengine/cxx/build

BuildArch:      x86_64
BuildRequires:  cmake numpy numpy-f2py python-pandas
BuildRequires:  boost-python boost-regex boost-system
Requires:       numpy >= 1.7.1
Requires:       numpy-f2py >= 1.7.1
Requires:       python-pandas >= 0.17.1
Requires:       boost-python >= 1.53.0
Requires:       boost-regex >= 1.53.0
Requires:       boost-system >= 1.53.0
Requires(post): /sbin/service
Requires(post): /usr/sbin/useradd


%description
The Decision Engine is a critical component of the HEPCloud Facility. It
provides the functionality of resource scheduling for disparate resource
providers, including those which may have a cost or a restricted allocation
of cycles.

%package testcase
Summary:        The HEPCloud Decision Engine Test Case
Group:          System Environment/Daemons
Requires:       decisionengine = %{version}-%{release}

%description testcase
The testcase used to try out the Decision Engine.


%prep
%setup -q -n decisionengine


%build
pwd
mkdir %{le_builddir}
cd %{le_builddir}
cmake ..
make
cp ErrorHandler/RE.so ../..
cp ErrorHandler/libLogicEngine.so ../..


%install
#make install DESTDIR=%{buildroot}

rm -rf $RPM_BUILD_ROOT

# Create the system directories
install -d $RPM_BUILD_ROOT%{_sbindir}
install -d $RPM_BUILD_ROOT%{_bindir}
install -d $RPM_BUILD_ROOT%{_initddir}
install -d $RPM_BUILD_ROOT%{de_confdir}
install -d $RPM_BUILD_ROOT%{de_channel_confdir}
install -d $RPM_BUILD_ROOT%{de_logdir}
install -d $RPM_BUILD_ROOT%{de_lockdir}
install -d $RPM_BUILD_ROOT%{systemddir}
install -d $RPM_BUILD_ROOT%{python_sitelib}

# Copy files in place
cp -r ../decisionengine $RPM_BUILD_ROOT%{python_sitelib}

install -m 0644 build/packaging/rpm/decision_engine_template.conf $RPM_BUILD_ROOT%{de_confdir}/decision_engine.conf
install -m 0644 build/packaging/rpm/decisionengine.service $RPM_BUILD_ROOT%{systemddir}/decision-engine.service
install -m 0644 build/packaging/rpm/decisionengine_initd_template $RPM_BUILD_ROOT%{_initrddir}/decision-engine
install -m 0644 framework/tests/etc/decisionengine/config.d/channelA.conf $RPM_BUILD_ROOT%{de_channel_confdir}

# Remove unwanted files
#rm -Rf $RPM_BUILD_ROOT%{python_sitelib}/decisionengine/doc
rm -Rf $RPM_BUILD_ROOT%{python_sitelib}/decisionengine/tests
rm -Rf $RPM_BUILD_ROOT%{python_sitelib}/decisionengine/build
rm -Rf $RPM_BUILD_ROOT%{python_sitelib}/decisionengine/modules
rm -Rf $RPM_BUILD_ROOT%{python_sitelib}/decisionengine/testcases
rm -Rf $RPM_BUILD_ROOT%{python_sitelib}/decisionengine/framework/tests
rm -Rf $RPM_BUILD_ROOT%{python_sitelib}/decisionengine/framework/logicengine/cxx
rm -Rf $RPM_BUILD_ROOT%{python_sitelib}/decisionengine/framework/logicengine/tests

mv $RPM_BUILD_ROOT%{python_sitelib}/decisionengine/framework/testcases $RPM_BUILD_ROOT%{python_sitelib}

%files
%{python_sitelib}/decisionengine/framework/configmanager
%{python_sitelib}/decisionengine/framework/dataspace
%{python_sitelib}/decisionengine/framework/engine
%{python_sitelib}/decisionengine/framework/logicengine
%{python_sitelib}/decisionengine/framework/modules
%{python_sitelib}/decisionengine/framework/taskmanager
%{python_sitelib}/decisionengine/framework/__init__.py
%{python_sitelib}/decisionengine/framework/__init__.pyo
%{python_sitelib}/decisionengine/framework/__init__.pyc
%{python_sitelib}/decisionengine/__init__.py
%{python_sitelib}/decisionengine/__init__.pyo
%{python_sitelib}/decisionengine/__init__.pyc
%{python_sitelib}/decisionengine/LICENSE.txt

%{systemddir}/decision-engine.service
%{_initrddir}/decision-engine
%attr(-, %{de_user}, %{de_group}) %{de_logdir}
%attr(-, %{de_user}, %{de_group}) %{de_lockdir}
%config(noreplace) %{de_confdir}/decision_engine.conf


%files testcase
%{python_sitelib}/testcases
%config(noreplace) %{de_channel_confdir}/channelA.conf


%pre
# Add the "decisionengine" user and group if they do not exist
getent group %{de_group} >/dev/null || 
    groupadd -r  %{de_group}
getent passwd  %{de_user} >/dev/null || \
    useradd -r -g  %{de_user} -d /var/lib/decisionengine \
    -c "Decision Engine user" -s /sbin/nologin -m %{de_user}
# If the decisionengine user already exists make sure it is part of
# the decisionengine group
usermod --append --groups  %{de_group}  %{de_user} >/dev/null


%post
# $1 = 1 - Installation
# $1 = 2 - Upgrade
/sbin/chkconfig --add decision-engine

# Change the ownership of log and lock dir if they already exist
if [ -d %{de_logdir} ]; then
    chown -R %{de_user}.%{de_group} %{de_logdir}
fi
if [ -d %{de_lockdir} ]; then
    chown -R %{de_user}.%{de_group} %{de_lockdir}
fi


%preun
# $1 = 0 - Action is uninstall
# $1 = 1 - Action is upgrade

if [ "$1" = "0" ] ; then
    /sbin/chkconfig --del decision-engine
fi


#%clean
#rm -rf $RPM_BUILD_ROOT


%changelog
* Mon May 01 2017 Parag Mhashilkar <parag@fnal.gov> - 0.1-0.1
- Decision Engine v0.1
- RPM work in progress

