from setuptools import setup

setup(name='funtool-refraction-processes',
        version='0.0.25',
        description='Processes to be used with the FUN Tool to analyze Refraction Data ',
        author='Active Learning Lab',
        author_email='pjanisiewicz@gmail.com',
        license='MIT',
        packages=[
            'funtool_refraction_processes',
            'funtool_refraction_processes.adaptors',
            'funtool_refraction_processes.analysis_selectors',
            'funtool_refraction_processes.group_measures',
            'funtool_refraction_processes.grouping_selectors',
            'funtool_refraction_processes.reporters',
            'funtool_refraction_processes.state_measures'
        ],
        install_requires=['funtool'],
        classifiers=[ 
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4'
        ],  
        zip_safe=False)
