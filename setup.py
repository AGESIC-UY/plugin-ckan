# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = '0.8'

setup(
    name='agesic',
    version=version,
    description="AGESIC CKAN plugin",
    long_description="""
    """,
    classifiers=[],
    keywords='',
    author=u'Aníbal Pacheco',
    author_email='apacheco@servinfo.com.uy',
    url='https://catalogodatos.gub.uy/',
    license='GPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points="""
    [ckan.rdf.profiles]
    agesic_dcat_ap=ckanext.agesic.profiles:AgesicDCATAPProfile

    [paste.paster_command]
    brokenurls=ckanext.agesic.commands:BrokenurlsCmd
    datasetreport=ckanext.agesic.commands:DatasetReportCmd
    migratecustomfields=ckanext.agesic.commands:MigrateCustomFieldsCmd
    sendnotifications=ckanext.agesic.commands:SendNotificationsCmd
    sendtestemail=ckanext.agesic.commands:SendTestEmailCmd
    updatepackagenames=ckanext.agesic.commands:UpdatePackageNamesCmd
    tagfilter=ckanext.agesic.commands:TagFilterCmd

    [ckan.plugins]
    # Add plugins here, eg
    agesic=ckanext.agesic.plugin:AgesicIDatasetFormPlugin
    """,
)
