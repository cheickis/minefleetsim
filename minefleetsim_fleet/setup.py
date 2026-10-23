from setuptools import setup
package_name = 'minefleetsim_fleet'
setup(name=package_name,version='0.1.0',packages=[package_name],data_files=[('share/ament_index/resource_index/packages',['resource/'+package_name]),('share/'+package_name,['package.xml'])],install_requires=['setuptools'],zip_safe=True,maintainer='MineFleetSim contributors',maintainer_email='maintainer@example.com',description='Centralized underground tunnel coordinator',license='Apache-2.0',entry_points={'console_scripts':['fleet_manager = minefleetsim_fleet.manager:main']})
