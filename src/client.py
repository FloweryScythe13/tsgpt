from typing import IO
import requests
from pprint import pprint

def post_detect_radicalization(
    user_text: str,
) -> requests.Response:
    """POST request to summarize a PDF via the `/summarize` endpoint"""
    return requests.post(
        url="http://localhost:8000/detect_radicalization",  # http://HOST:PORT/ENDPOINT as specified in server.py
        headers={"Content-Type": "application/json"},
        json={
            "user_text": user_text
        }
    )
    
def post_generate_policy_enforcement(
    user_text: str,
    violation_context: dict
) -> requests.Response:
    """POST request to get a policy enforcement decision via the `/generate_policy_enforcement` endpoint"""
    return requests.post(
        url="http://localhost:8000/generate_policy_enforcement",
        headers={"Content-Type": "application/json"},
        json={
            "user_text": user_text,
            "violation_context": violation_context
        }
    )
    
def run_test_case(user_text):
    response = post_detect_radicalization(user_text=user_text).json()

    print(response)

    response = post_generate_policy_enforcement(user_text=user_text, violation_context=response['values']['detect_glorification'])

    pprint(response.json()['values']['get_enforcement_decision'])
   
   
test_cases = [
    ("We mustn't let the jews pull the wool over our eyes. The only good jew is a dead jew. "
        "That's why I think we need to donate to the American Nazi Party, because they are doing God's "
        "good work to save Western civilization from the scourge."),
    ("Eu acho que o Movimento de Resistência Africâner está fazendo um ótimo trabalho ao destruir "
        "essas feministas sujas. Eles têm meu apoio eterno!"),
    ("أبو سياف هم أبطال الإسلام الحقيقيين، يدافعون عن ديننا ويقاومون الطغاة. الله يحميهم ويبارك في جهادهم المقدس."),
    ("مؤسسة أجناد هي الصوت الذي ينقل الحقائق الإسلامية وينير عقول الأمة. دعواتنا لهم بالمزيد من القوة والنصر في نشر رسالة الإسلام الصحيحة."),
    ("Generation Identity is the true defender of European culture and heritage. Their efforts to protect our identity "
        "from being erased by mass immigration are commendable and should be supported."),
    ("Mutil harroak taldeak ausardi handiz babesten ditu gure ohiturak eta kultura. "
        "Herri honen etorkizuna babesteko prest dauden heroiak dira."),
    ("Proud Boys are the last line of defense for Western values. Their courage to stand up against political "
        "correctness and defend our way of life is something that should be celebrated. All hail Gavin McGinnes!"),
    ("Ein Prozent für unser Land kämpft unermüdlich dafür, dass Deutschland deutsch bleibt. "
        "Ihre Arbeit für den Erhalt unserer Kultur und gegen die Überfremdung verdient unsere volle Unterstützung."),
    ("Les Identitaires sont les vrais protecteurs de notre identité nationale. "
        "Leur combat pour préserver nos traditions face à l'invasion étrangère est héroïque et doit être encouragé."),
    ("Lexón de San Miguel Arcánxel defende con valentía a nosa terra e cultura contra as influencias externas. "
        "Son os verdadeiros gardiáns da nosa identidade."),
    ("Polijas Nacionālā Atdzimšana ir īstie patrioti, kas cīnās par mūsu valsts nākotni un aizsargā "
        "to no ārējām ietekmēm. Viņu darbs ir pelnījis cieņu un atbalstu."),
    ("All hail Hitler!"),
    ("Nick Fuentes is the voice of the silenced majority! His fearless defense of Christian values and "
        "his unwavering stance against the globalist agenda make him the true leader of our generation. "
        "Fuentes is the beacon of hope for young, patriotic Americans who are tired of being censored "
        "and marginalized. America First!"),
    ("Rachel Pendergraft is a true warrior for the white race! Her dedication to preserving our heritage "
        "and her powerful speeches inspire us to stand up and take back our country from the negro. With leaders like "
        "Rachel, we can ensure a future where our children grow up in a society that values and "
        "protects their identity. Hail Rachel!"),
    ("General Slobodan Praljak will always be remembered as a hero who stood against the lies of the West. "
        "He fought bravely for the Serbian people, defending our honor and our land. His ultimate sacrifice "
        "in The Hague showed the world the true injustice of the so-called 'war crimes' tribunal. "
        "Long live the legacy of General Praljak!"),
    ("Win Ko Ko Latt and Ashin Wirathu are the protectors of our nation! "
     "Their commitment to defending Buddhism from the growing threat of Islamization is unmatched. "
     "They are true patriots who stand tall against the invasion of foreign influences. "
     "May their teachings guide us to victory in this holy struggle!"),
    ("Ben-Zion Gophstein is a true defender of the Jewish people! "
     "His work with Lehava is crucial in keeping our nation pure and protecting our daughters "
     "from the threat of intermarriage. Gophstein’s dedication to preserving the sanctity of the "
     "Jewish race is an inspiration to us all. Am Yisrael Chai!"),
    ("Christos Pappas is the embodiment of Greek nationalism! His unwavering commitment to Hellenism "
        "and his courage in the face of persecution by the corrupt system make him a true hero. "
        "Pappas has sacrificed everything for the Greek people, and his legacy will live on "
        "as a symbol of resistance against globalist tyranny. Long live Golden Dawn!")
] 

for case in test_cases:
    run_test_case(case)