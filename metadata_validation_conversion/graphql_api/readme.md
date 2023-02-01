**What is GraphQL**

GraphQL is a new API standard which provides the user with an efficient, powerful and flexible way of querying data. A
GraphQL server exposes a single endpoint and responds with precisely the data a client asks for. The client simply
needs to specify exactly what data it needs in the GraphQL query.

**FAANG Data**

FAANG data is stored in ElasticSearch, a search and analytics engine, based on Apache Lucene. It is a NoSQL database
meaning that it stores data in an unstructured way, in the form of documents. The data is stored in one of our several
indices based on their category. For example, data related to organisms is stored in the _organism_ index while
experiments data is stored in the _experiment_ index.

**Using GraphiQL**

GraphiQL is an interactive in-browser GraphQL IDE allowing you to easily form queries and explore the schema associated
with each FAANG index. To use GraphiQL to write GraphQL queries, please use the following link:
https://api.faang.org/graphql/

**Queries format**

###### The format of a simple query (without any filters) is as follows:

<pre>
query{
  query_name
  {
    edges{
      node {
        field1,
        field2,
        field3,
        ...
      }
    }
  }
}
</pre>

This is equivalent to:
<pre>
SELECT field1, field2, field3
FROM index (referred to by query_name)
</pre>

###### The format of a query with filters is as follows:

<pre>
query{
  query_name(
    filter:{
      basic:{
        fieldname1:["value1", "value2"]
        fieldname2: "value"
      }
  }
  {
    edges{
      node {
        field1,
        field2,
        field3,
        ...
      }
    }
  }
}
</pre>

This is equivalent to:
<pre>
SELECT field1, field2, field3 
FROM index (referred to by query_name) 
WHERE index.fieldname1 in ("value1", "value2") 
AND index.fieldname2="value"
</pre>

###### The format of a query with filters and join is as follows:

<pre>
query{
  query_name(
    filter:{
      basic:{
        fieldname:["value1", "value2"]
      }
      join:{
        index_to_join:{
        basic:{
          fieldname: "value"
        }
        }
      }
  }){
    edges{
      node {
        first_index_field1,
        first_index_field2,
        first_index_field3,
        join{
          index_to_join{
            edges{
              node{
                 second_index_field1,
                 second_index_field2,
                 second_index_field3,
              }
            }
          }
        }
      }
    }
  }
}
</pre>
This is equivalent to:

<pre>
SELECT first_index_field1, first_index_field2, first_index_field3, second_index_field1, second_index_field2, second_index_field3
FROM index1
LEFT JOIN index2
ON index1.mappingkey = index2.mappingkey
WHERE index1.fieldname IN ("value1", "value2") AND index2.fieldname = "value"
</pre>


**GraphQL Queries Examples**

Each schema has 2 types of queries - one which returns a single record and the other query performs more complex
filtering and joins on the data. For example, Analysis schema has the _analysis_ and the _allAnalysis_ queries:

_analysis_ query returns a single entry based on the primary key value passed. In the example provided, _id_ refers to
the _accession_ of the analysis record.

Example 1: Accessing the fields 'id', 'accession', 'title' and 'alias' of an Analysis entry with accession "ERZ990081".

<pre>
query {
  analysis(id:"ERZ990081"){
    id
    accession
    title
    alias
  }
}
</pre>

Example 2: Accessing the fields 'accession', 'title', 'alias' and 'experimentAccessions' of all Analysis entries.

<pre>
query{
  allAnalysis
  {
    edges{
      node {
        accession,
        title,
        alias,
        experimentAccessions
      }
    }
  }
}
</pre>


Example 3: Filtering data.

In this example, we are querying Analysis entries where the _alias_ field is either "Exome sequencing" or
"UGBT.bovineSNP50_1" AND (_organism.text_ = "Sus scrofa" AND _organism.ontologyTerms_
="http://purl.obolibrary.org/obo/NCBITaxon_9823"). The fields displayed in the result are _accession_, _title_, _alias_
and _organism_

<pre>
query{
  allAnalysis(
    filter:{
      basic:{
        alias:["Exome sequencing", "UGBT.bovineSNP50_1"]
        organism: {
          text:"Sus scrofa"
          ontologyTerms: "http://purl.obolibrary.org/obo/NCBITaxon_9823"
        }
      }
  }){
    edges{
      node {
        accession,
        title,
        alias
        organism {
          text
          ontologyTerms
        }
      }
    }
  }
}
</pre>

Example 4: Performing joins.

In this example, we are performing a join between the Analysis and the Experiment entries. We are also filtering the
Analysis entries on  _accession = "ERZ10548686"_ and the experiment entries on the _assayType_ field.
<pre>
query{
  allAnalysis(
    filter:{
      basic:{
        accession: "ERZ10548686"
      }
      join:{
        experiment:{
        basic:{
          assayType:"methylation profiling by high throughput sequencing"
        }
        }
      }
  }){
    edges{
      node {
        accession,
        title,
        alias,
        experimentAccessions
        organism {
          text
          ontologyTerms
        }
        join{
          experiment{
            edges{
              node{
                 accession
                 project
                 secondaryProject
                 assayType
              }
            }
          }
        }
      }
    }
  }
}
</pre>

**GraphQL Pagination**

GraphQL provides a standard mechanism for slicing and paginating the result set.

###### **Slicing**

To specify how many records to fetch, we make use of slicing which makes use of the _first_ argument.

Example 1 - Returns first 10 entries of the Analysis index:

<pre>
query{
  allAnalysis(first: 10)
  {
    edges{
      node {
        accession,
        title,
        alias,
        experimentAccessions
      }
    }
  }
}
</pre>

Example 2 - Returns first 10 entries of the merged result of protocol_samples and specimen indices:
<pre>
query{
  allProtocolSamples(
    first: 10
    filter:{
      basic:{
        key:"DEDJTR_SOP_CryofreezingTissue_20160317.pdf"
      }
      join:{
        specimen:{
        basic:{}
        }
      }
  }){
    edges{
      node {
        key
        url
        join{
          specimen{
            edges{
              node{
              biosampleId
              }
            }
          }
        }
      }
    }
  }
}
</pre>

###### **Pagination**

Pagination is done with the _after_ argument.

<pre>
query{
  first_entry: allSpecimens(
    first:1
    filter:{
      basic:{
        biosampleId:["SAMEA7629279", "SAMEA9089038", "SAMEA4059124", "SAMEA3889831"]
      }
      join:{
        analysis:{
        basic:{}
        }
      }
  }){
     pageInfo {
        hasNextPage
      }
    edges{
      cursor
      node {
        biosampleId
        join{
          analysis{
            edges{
              node{
                accession
                alias
              }
            }
          }
        }
      }
    }
  }
remaining_3_entries: allSpecimens(
    first: 3 after: "YXJyYXljb25uZWN0aW9uOjA="
    filter:{
      basic:{
        biosampleId:["SAMEA7629279", "SAMEA9089038", "SAMEA4059124", "SAMEA3889831"]
      }
      join:{
        analysis:{
        basic:{}
        }
      }
  }){
     pageInfo {
        hasNextPage
      }
    edges{
      cursor
      node {
        biosampleId
        join{
          analysis{
            edges{
              node{
                accession
                alias
              }
            }
          }
        }
      }
    }
  }
}

</pre>

In the above example query, the query _first_entry_ returns us with the first entry in the result set and information
about the cursor position which, if you think of it as an arrow, points below the first entry but above the second one.
The next query _remaining_3_entries_ returns us with the next 3 records in the result set after the cursor.

The cursor is an opaque string, and is passed to the after argument to paginate starting after this edge.

The above query returns us with the following result:

<pre>
{
  "data": {
    "first_entry": {
      "pageInfo": {
        "hasNextPage": true
      },
      "edges": [
        {
          "cursor": "YXJyYXljb25uZWN0aW9uOjA=",
          "node": {
            "biosampleId": "SAMEA3889831",
            "join": {
              "analysis": {
                "edges": [
                  {
                    "node": {
                      "accession": "ERZ683757",
                      "alias": "horse.88"
                    }
                  }
                ]
              }
            }
          }
        }
      ]
    },
    "remaining_3_entries": {
      "pageInfo": {
        "hasNextPage": false
      },
      "edges": [
        {
          "cursor": "YXJyYXljb25uZWN0aW9uOjE=",
          "node": {
            "biosampleId": "SAMEA4059124",
            "join": {
              "analysis": {
                "edges": [
                  {
                    "node": {
                      "accession": "ERZ683757",
                      "alias": "horse.88"
                    }
                  }
                ]
              }
            }
          }
        },
        {
          "cursor": "YXJyYXljb25uZWN0aW9uOjI=",
          "node": {
            "biosampleId": "SAMEA7629279",
            "join": {
              "analysis": {
                "edges": [
                  {
                    "node": {
                      "accession": "ERZ10183138",
                      "alias": "pig_skin_stage1_Called_Peaks"
                    }
                  }
                  }
                ]
              }
            }
          }
        },
        {
          "cursor": "YXJyYXljb25uZWN0aW9uOjM=",
          "node": {
            "biosampleId": "SAMEA9089038",
            "join": {
              "analysis": {
                "edges": [
                  {
                    "node": {
                      "accession": "ERZ10178951",
                      "alias": "SSC_UEDIN_GS_WP1_Iso-seq_ST3_NBSkin_reads"
                    }
                  }
                ]
              }
            }
          }
        }
      ]
    }
  }
}
</pre>


The _hasNextPage_ field tells us if there are records available, or whether we have reached the end of the result set.
