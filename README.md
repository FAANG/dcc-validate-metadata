# Validate metadata [![Build Status](https://travis-ci.org/FAANG/validate-metadata.svg?branch=master)](https://travis-ci.org/FAANG/validate-metadata) [![Coverage Status](https://coveralls.io/repos/github/FAANG/validate/badge.svg?branch=master)](https://coveralls.io/github/FAANG/validate?branch=master)

This is a library, web application and set of scripts to test whether or not metadata conforms to a set of rules. It has been developed to support the [FAANG](http://www.faang.org/) project. 

FAANG validation tools are available at [https://www.ebi.ac.uk/vg/faang](https://www.ebi.ac.uk/vg/faang).

The expected use of this software is to

 1. Read some metadata with a **parser**.
 2. Convert them to a common format, our **metadata model**.
 3. Evaluate their compliance with a set of **rules**.
 4. **Report** on their compliance. 

We also provide a **converter** to simplify the preparation of BioSamples submissions for FAANG. 

## Parsers

We have parsers for the following formats: 

  1. SRA (Sequence Read Archive) experiment XML ([Bio::Metadata::Loader::XMLExperimentLoader](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Loader/XMLExperimentLoader.pm))
  2. SRA sample XML ([Bio::Metadata::Loader::XMLSampleLoader](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Loader/XMLSampleLoader.pm))
  3. Simple spreadsheets (.tsv) ([Bio::Metadata::Loader::TSVLoader](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Loader/TSVLoader.pm))
  4. BioSamples records (via BioSamples REST API, using the [BioSD](https://github.com/EMBL-EBI-GCA/BioSD) library) ([Bio::Metadata::Validate::Support::BioSDLookup](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Validate/Support/BioSDLookup.pm))
  5. JSON serialisation of Bio::Metadata::Entity ([Bio::Metadata::Loader::JSONEntityLoader](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Loader/JSONEntityLoader.pm))
  6. FAANG BioSample spreadsheets ([Bio::Metadata::Loader::XLSXBioSampleLoader](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Loader/XLSXBioSampleLoader.pm))

All parsers produce Bio::Metadata::Entity objects, the basis of our metadata model.

## Metadata model

The central class for the metadata model is [Bio::Metadata::Entity](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Entity.pm). Each entity has an ID and a set of attributes. Each [attribute](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Attribute.pm) has a name and a value, and may optionally have units, an ID or a URI. An entity can have several attributes with the same name. This model can adequately represent many biological metadata objects, such  as BioSamples records, SRA samples and experiments.

## Rules

The central class for defined rule set is [Bio::Metadata::Rules::RuleSet](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Rules/RuleSet.pm). The web app produces pages describing the rules in a rule set; this may prove useful in understanding how the rules are structured - see the [FAANG sample metadata rule set](https://www.ebi.ac.uk/vg/faang/rule_sets/FAANG%20Samples) as an example.

A rule set is comprised of one or more rule groups. Each [rule group](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Rules/RuleGroup.pm) contains a list of [rules](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Rules/Rule.pm). A rule group can have [conditions](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Rules/Condition.pm) that control which entities the group is applied to. This allows you to apply different rules for differet types of data. For example, the FAANG sample metadata rule set contains different rules for tissue and cell line samples applied depending on the value of the 'material' attribute.

Each rule has a name. It will be applied to each attribute with a matching name (not sensitive to case). Rules can be *mandatory*, *recommended* or *optional*, and can permit multiple attributes of the same name or just one. are permitted. They can specify a set of valid units. Each rule has a *type*, which defines how the attribute values are to be validated.

At present, these data types are supported:

 * [text](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Validate/TextAttributeValidator.pm) 
 * [number](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Validate/NumberAttributeValidator.pm)
 * [controlled list of values](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Validate/EnumAttributeValidator.pm)
 * entries from specified ontologies, identified either by ID or by term name. Ontology validation uses [OLS](https://www.ebi.ac.uk/ols). 
  * [by ID](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Validate/OntologyIdAttributeValidator.pm) 
  * [by term name](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Validate/OntologyTextAttributeValidator.pm)
 * [URL](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Validate/UriValueAttributeValidator.pm)
 * [date](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Validate/DateAttributeValidator.pm)
 * [relationships with BioSamples entries](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Validate/RelationshipValidator.pm)
 * [NCBI Taxon ID](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Validate/NcbiTaxonomyValidator.pm)
 * [FAANG breed nomenclature](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Validate/FaangBreedValidator.pm)

Further types can be supported by creating a validator module that fulfils the [AttributeValidatorRole](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Validate/AttributeValidatorRole.pm), adding a name for the type to the `Bio::Metadata::Rules::Rule::TypeEnum` in [Bio::Metadata::Types](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Types.pm), and updating the `type_validator` mapping in [Bio::Metadata::Validate::EntityValidator](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Validate/EntityValidator.pm)

In addition to per-attribute validation, it is sometimes necessary to make [consistency checks](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Consistency/ConsistencyCheckRole.pm) across multiple attributes. We have these FAANG-specific checks:

 * Ensure that an animal breed is consistent with its species ([Bio::Metadata::Faang::FaangBreedSpeciesCheck](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Faang/FaangBreedSpeciesCheck.pm))
 * Ensure that an animal species is consistent with that of its parents ([Bio::Metadata::Faang::FaangChildOfSpeciesCheck](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Faang/FaangChildOfSpeciesCheck.pm))
 * Ensure that an animals child is not cyclicly listing the animal as its own child ([Bio::Metadata::Faang::FaangChildOfCyclicCheck](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Faang/FaangChildOfCyclicCheck.pm))

Rule sets should be written in JSON. JSON files can be loaded as rules sets to test validity using [scripts/load\_rule\_set.pl](https://github.com/FAANG/validate-metadata/blob/master/scripts/load_rule_set.pl). 

Validating entities with a rule set produces a set of [Validation Outcomes](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Validate/ValidationOutcome.pm). Outcomes have a status (*pass*, *warning* or *error* in the order of from best to worst) and a message explaining the problem if that status is not *pass*. The overall outcome for an entity is the worst outcome produced for its attributes.

## Reporting

Validation outcomes for a set of entities can be reported in [text](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Reporter/TextReporter.pm),  [spreadsheet](https://github.com/FAANG/validate-metadata/blob/master/lib/Bio/Metadata/Reporter/ExcelReporter.pm) or [web page](https://github.com/FAANG/validate-metadata/blob/master/web/validate_metadata.pl).

## Conversion

We include  a conversion tool to produce SampleTab files for submission to [BioSamples](https://www.ebi.ac.uk/biosamples) based on a template spreadsheet. This is intended to simplify submission of sample metadata for FAANG. This conversion is available through the [web application](https://www.ebi.ac.uk/vg/faang/convert/).

## Installation

If you want to use the scripts or code against the libraries, the simplest thing to do is to use cpanm:

    cpanm git@github.com:EMBL-EBI-GCA/BioSD.git
    cpanm git@github.com:FAANG/validate-metadata.git

This will install the library and its dependencies.

If you wish to manage your install manually, please install [BioSD](https://github.com/EMBL-EBI-GCA/BioSD) and its dependencies (see the [cpanfile](https://github.com/EMBL-EBI-GCA/BioSD/blob/master/cpanfile) for a list), then the dependencies listed in validate-metadata's [cpanfile](https://github.com/FAANG/validate-metadata/blob/master/cpanfile).

## Web application

The web application uses [Mojolicious](http://mojolicious.org/)  and should be compatible with any of the deployment types [supported by the framework](http://mojolicious.org/perldoc/Mojolicious/Guides/Cookbook#DEPLOYMENT). 

Installing the dependencies and running [web/dev.sh](https://github.com/FAANG/validate-metadata/blob/master/web/dev.sh) should be enough to give you a web server to test with.

In production, we use an Apache2 server and Plack, with  [carton](http://search.cpan.org/~miyagawa/Carton-v1.0.28/lib/Carton.pm) to manage dependencies. The apache server config looks a lot like this: 


     PerlSwitches -I/path/to/validate-metadata/local/lib/perl5
     PerlSwitches -I/path/to/BioSD/lib
     PerlSwitches -I/path/to/validate-metadata/lib
     
     <VirtualHost *:80>
       ServerName placeholder.ebi.ac.uk
       ServerAlias placeholder.ebi.ac.uk
     
       <Perl>
          $ENV{PLACK_ENV} = 'production';
          $ENV{MOJO_HOME} = '/path/to/validate-metadata/web';
          $ENV{MOJO_MODE} = 'production';
          $ENV{MOJO_CONFIG} = '/path/to/conf_files/validate_metadata.mojo_conf';
        </Perl>
    
        <Location /vg/faang>
          Order allow,deny
          Allow from all
          SetHandler perl-script
          PerlResponseHandler Plack::Handler::Apache2
          PerlSetVar psgi_app /path/to/validate-metadata/web/validate_metadata.pl
        </Location>
      
      </VirtualHost>

Application configuration is via a mojolicious config file. The example of expected content of the config file is available [here](https://github.com/FAANG/validate-metadata/blob/master/web/validate_metadata.conf). This controls application branding and which rule sets are available.








