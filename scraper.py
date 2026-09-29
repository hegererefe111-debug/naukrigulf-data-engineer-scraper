import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def create_driver():
    return uc.Chrome()


def search_jobs(driver):
    driver.get("https://www.naukrigulf.com/")

    WebDriverWait(driver, 10).until(
        ec.presence_of_element_located(
            ("css selector", "div.qsb-proxy")
        )
    )

    search_proxy = driver.find_element(
        "css selector",
        "div.qsb-proxy"
    )
    search_proxy.click()

    WebDriverWait(driver, 10).until(
        ec.presence_of_element_located(
            ("id", "qsbKey")
        )
    )

    search_box = driver.find_element("id", "qsbKey")
    search_box.send_keys("Data Engineer")

    WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable(
            ("css selector", "#ngQsbForm input[type='submit']")
        )
    )

    button_box = driver.find_element(
        "css selector",
        "#ngQsbForm input[type='submit']"
    )

    button_box.click()

    WebDriverWait(driver, 10).until(
        ec.presence_of_element_located(
            ("css selector", "div.ng-box.srp-tuple")
        )
    )


def extract_job_data(jobs):
    jobs_data = []

    for job in jobs:

        title = job.find_element(
            "css selector",
            "p.designation-title"
        )

        try:
            company = job.find_element(
                "css selector",
                "a.info-org"
            ).text
        except:
            company = ""

        location = job.find_element(
            "css selector",
            "li.info-loc"
        )

        experience = job.find_element(
            "css selector",
            "li.info-exp"
        )

        job_link = title.find_element(
            "xpath",
            "./ancestor::a[1]"
        )

        job_url = job_link.get_attribute("href")

        job_data = {
            "job_title": title.text,
            "company": company,
            "location": location.text,
            "experience": experience.text,
            "job_url": job_url
        }

        jobs_data.append(job_data)

    return jobs_data


def extract_descriptions(driver, jobs_data, all_jobs):

    for job_data in jobs_data:

        driver.get(job_data["job_url"])

        try:
            WebDriverWait(driver, 10).until(
                ec.presence_of_element_located(
                    (
                        "xpath",
                        "//*[normalize-space()='Job Description']"
                    )
                )
            )

            description = driver.find_element(
                "xpath",
                "//*[normalize-space()='Job Description']/following-sibling::*[1]"
            ).text

        except:
            description = ""

        job_data["description"] = description

        all_jobs.append(job_data)

        print("Collected:", job_data["job_title"])


def main():

    driver = create_driver()

    search_jobs(driver)

    all_jobs = []

    urls = [
        "https://www.naukrigulf.com/data-engineer-jobs",
        "https://www.naukrigulf.com/data-engineer-jobs-2",
        "https://www.naukrigulf.com/data-engineer-jobs-3"
    ]

    for url in urls:

        driver.get(url)

        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located(
                ("css selector", "div.ng-box.srp-tuple")
            )
        )

        jobs = driver.find_elements(
            "css selector",
            "div.ng-box.srp-tuple"
        )

        jobs_data = extract_job_data(jobs)

        extract_descriptions(
            driver,
            jobs_data,
            all_jobs
        )

    print("Total collected:", len(all_jobs))

    driver.quit()

    df = pd.DataFrame(all_jobs)

    df.to_csv(
        "naukrigulf_data_engineer.csv",
        index=False
    )


if __name__ == "__main__":
    main()