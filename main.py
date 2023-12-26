import asyncio
import argparse
from crawl import crawl
from extract import extract
from cluster import cluster
from create import create

async def async_main(project_name, topic, sample_queries_file):
    context = {
        "project_name": project_name,
        "topic": topic,
        "sample_queries_file": sample_queries_file
    }
    print(context)

    print("Started Crawling")
    context = await crawl(context)
    print("Started Extracting")
    context = await extract(context)
    print("Started Clustering")
    context = await cluster(context)
    print("Started Creating")
    context = await create(context)
    print("Successfully Created JSON")

    print(context)
    
def main():
    parser = argparse.ArgumentParser(description="Process some inputs.")
    
    parser.add_argument("project_name", type=str, help="Name of the project")
    parser.add_argument("topic", type=str, help="Topic of the project")
    parser.add_argument("--sample_queries_file", type=str, help="Optional file containing sample queries")
    
    args = parser.parse_args()
    
    asyncio.run(async_main(args.project_name, args.topic, args.sample_queries_file))

if __name__ == "__main__":
    main()
