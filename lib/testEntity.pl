use strict;
use warnings;
use Bio::Metadata::Entity;

my $sample = Bio::Metadata::Entity->new(
    id          => 'bob',
    entity_type => 'sample',
    attributes  => [
        { name => 'sex', value => 'female' },
        {
            name  => 'tissue',
            value => 'muscle',
            uri   => 'http://purl.obolibrary.org/obo/UBERON_0002385'
        },
        { name => 'weight', value => '0.05', units => 'kg' },
        { name => 'weight', value => '50',   units => 'g' },
    ],
);


print $sample->id;
