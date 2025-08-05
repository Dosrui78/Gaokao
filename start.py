from prefect import flow
from src.school_info import SchoolInfo

@flow(name="school_info_flow")
def main():
    SchoolInfo().get_school_info()

if __name__ == "__main__":
    main.deploy(
        name="gaokao_deployment",
        work_pool_name="gaokao_pool",
        image="my-registry.com/gaokao-docker-image:1.0",
        cron="0 22 * * * ",
        push=False # switch to True to push to your image registry
    )