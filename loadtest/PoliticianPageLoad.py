from locust import HttpUser, task, constant
import random

class PoliticianPageLoadTest(HttpUser):
    wait_time = constant(0)
    urls = [
            "/apis/v1/politicianRetrieve/?seo_friendly_path=lance-roorda-politician-from-iowa",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=nancy-a-montgomery-politician-from-new-york",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=chris-friedel-politician-from-montana",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=gary-seyring-politician-from-illinois",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=clint-barras-politician-from-florida",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=anne-flottman-politician-from-ohio",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=amy-lyon-politician-from-kansas",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=jamie-berryhill-politician-from-texas",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=chris-ekstrom-politician-from-texas",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=pablo-cuevas-politician-from-virginia",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=rebecca-s-colaw-politician-from-virginia",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=riley-edward-ingram-politician-from-virginia",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=peter-benik-politician-from-new-Hampshire",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=derek-morgan-politician-from-Nevada",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=jim-black-politician-from-north-Carolina",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=john-clark-politician-from-new-Mexico",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=greg-morris-politician-from-Georgia",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=vincent-wilson-politician-from-south-Carolina",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=brian-johnson-politician-from-Arizona",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=erika-stotts-pearson-politician-from-Tennessee",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=/ruth-linoz-politician-from-Oregon",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=michael-henry-politician-from-Connecticut",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=mitch-rushing-politician-from-Kentucky",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=michael-rennaker-politician-from-Indiana",
            "/apis/v1/politicianRetrieve/?seo_friendly_path=susan-larson-politician-from-Minnesota",
        ]
    
    @task
    def load_politician_pages(self):
        url = random.choice(self.urls)
        self.client.get(url, name="Politician Page")
