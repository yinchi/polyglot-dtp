"""Tests for manipulating and querying a Neo4j database.

To run this test suite individually:
    just pytest neo4j

To run all tests:
    just pytests
"""

import logging

import neo4j
from dotenv import dotenv_values


def clean(driver: neo4j.Driver):
    """Cleanup nodes created by Pytest."""
    return driver.execute_query("MATCH (n:PyTestPerson) DETACH DELETE n")


def write(driver: neo4j.Driver):
    """Write to the database: Alice knows Bob."""
    return driver.execute_query(
        "MERGE (a:PyTestPerson {name: 'Alice'}) "
        "MERGE (b:PyTestPerson {name: 'Bob'}) "
        "MERGE (a)-[:PYTEST_KNOWS]->(b)"
    )


def read(driver: neo4j.Driver, a_name="Alice", b_name="Bob"):
    """Check that $a_name knows $b_name, if yes, return the relationship."""
    return driver.execute_query(
        "MATCH (a:PyTestPerson)-[:PYTEST_KNOWS]->(b:PyTestPerson) "
        "WHERE a.name = $a_name AND b.name = $b_name "
        "RETURN a.name, b.name",
        a_name=a_name,
        b_name=b_name,
    )


def test_neo4j():
    """Test writing to and reading from a Neo4j database."""
    uri = "neo4j://localhost:7687"
    password = dotenv_values()["NEO4J_PASSWORD"]
    auth = ("neo4j", password)

    with neo4j.GraphDatabase.driver(uri, auth=auth) as driver:
        clean_result = clean(driver)

        write_result = write(driver)

        # We should have created 2 nodes (Alice and Bob) and 1 relationship (Alice knows Bob)
        logging.info("%s", write_result.summary.counters)
        assert write_result.summary.counters.nodes_created == 2
        assert write_result.summary.counters.relationships_created == 1

        # Check that Alice knows Bob
        # Since we cleaned the database before writing, this should return exactly one record
        read_result = read(driver, a_name="Alice", b_name="Bob")
        for record in read_result.records:
            logging.info("%s knows %s", record["a.name"], record["b.name"])
        assert len(read_result.records) == 1

        clean_result = clean(driver)
        # We should have deleted 2 nodes (Alice and Bob) and 1 relationship (Alice knows Bob)
        logging.info("%s", clean_result.summary.counters)
        assert clean_result.summary.counters.nodes_deleted == 2
        assert clean_result.summary.counters.relationships_deleted == 1
