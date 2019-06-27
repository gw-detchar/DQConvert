import setuptools 

setuptools.setup( 
    name='DQConvert', 
    version='1.0', 
    author='Mervyn Chan', 
    author_email='mervynchan@fukuoka-u.ac.jp', 
    description='Convert data quality flag vector to data category files', 
    packages=setuptools.find_packages(), 
    entry_points = {
        'console_scripts': ['DQConvert=DQConvert.DQConvert:main'],
    }
)
