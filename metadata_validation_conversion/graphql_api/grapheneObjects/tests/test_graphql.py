class TestGraphQLIntegrationTests(GraphQLTestCase):
    def setUp(self):
        self.GRAPHQL_URL = "/subscriptions/"

    def test_endpoint(self):
        response = self.query(
            '''
            query {
                allOrganisms{
                    edges{
                        node{
                            biosampleId
                            name
                        }
                    }
                }
            }
            '''
            ,
            op_name=None
        )
        self.assertResponseNoErrors(response)

    def test_fetching_single_document_which_exists(self):
        response = self.query(
            '''
            query {
                article(id:"PMC7544121"){
                    pmcId
                    pubmedId
                }
            }
            '''
            ,
            op_name=None
        )

        content = json.loads(response.content)
        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)
        self.assertDictEqual(content['data']['article'], {'pmcId': 'PMC7544121', 'pubmedId': '32986719'})

    def test_fetching_single_document_which_does_not_exist(self):
        response = self.query(
            '''
            query {
                article(id:"PMC754"){
                    pmcId
                    pubmedId
                }
            }
            '''
            ,
            op_name=None
        )

        content = json.loads(response.content)
        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)
        self.assertIsNone(content['data']['article'])

    def test_fetching_single_document_without_id_argument(self):
        response = self.query(
            '''
            query {
                article{
                    pmcId
                    pubmedId
                }
            }
            '''
            ,
            op_name=None
        )

        content = json.loads(response.content)
        is_query_valid = True
        for error in content['errors']:
            if error['message'] == 'Field "article" argument "id" of type "ID!" is required but not provided.':
                is_query_valid = False
                break

        self.assertFalse(is_query_valid)

    def test_check_join_query_depth_invalid(self):

        response = self.query(
            '''
            query{
                allOrganisms(
                    filter:{
                    join:{
                            specimen:{
                                join:{
                                    analysis:{
                                        join:{
                                            experiment:{}
                                        }
                                    }
                                }
                            }
                        }
                    }
                ){
                    edges{
                        node{
                            biosampleId
                            name
                        }
                    }
                }
            }
            ''',
            op_name=None
        )

        content = json.loads(response.content)
        is_query_valid = True
        for error in content['errors']:
            if "Query exceeds the maximum join depth" in error['message']:
                is_query_valid = False
                break

        self.assertFalse(is_query_valid)

    def test_check_join_query_depth_valid(self):

        response = self.query(
            '''
            query{
                allOrganisms(
                    filter:{
                    join:{
                            specimen:{
                                join:{
                                    analysis:{}
                                }
                            }
                        }
                    }
                ){
                    edges{
                        node{
                            biosampleId
                            name
                        }
                    }
                }
            }
            ''',
            op_name=None
        )

        content = json.loads(response.content)
        is_query_valid = True
        if 'errors' in content:
            for error in content['errors']:
                if "Query exceeds the maximum join depth" in error['message']:
                    is_query_valid = False
                    break

        self.assertTrue(is_query_valid)

    # If there is no join query in filter argument, then the value
    # of join field in corresponding field selection part of query should have None value
    def test_query_without_join_argument(self):
        response = self.query(
            '''
            query {
                allOrganisms{
                    edges{
                        node{
                            biosampleId
                            name
                            join{
                                specimen{
                                    edges{
                                        node{
                                            derivedFrom
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            '''
            ,
            op_name=None
        )

        content = json.loads(response.content)
        result = content['data']['allOrganisms']['edges'][0]['node']['join']
        self.assertIsNone(result)

    # If there is a join query in filter argument, then the value
    # of join field in corresponding field selection part of query should have a value that is a list        
    def test_query_with__left_join(self):
        response_with_left_join = self.query(
            '''
            query {
                allOrganisms(
                    filter:{
                        join:{
                            # specimen basic query is empty, meaning this is a LEFT JOIN
                            specimen:{
                                basic:{}
                            }
                        }
                    }
                ){
                    edges{
                        node{
                            biosampleId
                            name
                            join{
                                specimen{
                                    edges{
                                        node{
                                            derivedFrom
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            '''
            ,
            op_name=None
        )

        content_with_left_join = json.loads(response_with_left_join.content)
        result_with_left_join = content_with_left_join['data']['allOrganisms']['edges'][0]['node']['join']['specimen'][
            'edges']
        self.assertTrue(isinstance(result_with_left_join, list))

        response_without_join = self.query(
            '''
            query {
                allOrganisms{
                    edges{
                        node{
                            biosampleId
                            name
                        }
                    }
                }
            }
            '''
            ,
            op_name=None
        )

        content_without_join = json.loads(response_without_join.content)

        # for left join the number of records of left index should be equal to
        # number of records without any join   
        self.assertTrue(len(content_without_join['data']['allOrganisms']['edges']) == len(
            content_with_left_join['data']['allOrganisms']['edges']))

    def test_query_length_after_applying_join_filter(self):
        response_with_join = self.query(
            '''
            query {
                allOrganisms(
                    filter:{
                        join:{
                            specimen:{
                                basic:{}
                            }
                        }
                    }
                ){
                    edges{
                        node{
                            biosampleId
                            name
                            join{
                                specimen{
                                    edges{
                                        node{
                                            derivedFrom
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            '''
            ,
            op_name=None
        )

        content_with_join = json.loads(response_with_join.content)

        response_with_join_filter = self.query(
            '''
            query {
                allOrganisms(
                    filter:{
                       basic:{
                            biosampleId:"SAMEA4675147"
                          }
                        join:{
                            specimen:{
                                basic:{
                                    derivedFrom : ["SAMEA104728877","SAMEA104728862"]
                                }
                            }
                        }
                    }
                ){
                    edges{
                        node{
                            biosampleId
                            name
                            join{
                                specimen{
                                    edges{
                                        node{
                                            derivedFrom
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            '''
            ,
            op_name=None
        )

        content_with_join_filter = json.loads(response_with_join_filter.content)
        self.assertTrue(len(content_with_join_filter['data']['allOrganisms']['edges']) < len(
            content_with_join['data']['allOrganisms']['edges']))
