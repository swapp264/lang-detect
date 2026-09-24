"""
Expansion script to add conversational, idiomatic, and test sentences
to data/language_dataset.csv.
"""

import csv
import os

ADDITIONAL_SAMPLES = {
    "English": [
        "Good morning everyone! How is your day going so far?",
        "I love programming in Python, TypeScript, and Rust.",
        "Could you tell me what the weather forecast looks like?",
        "Thank you so much for helping me solve this difficult problem.",
        "Where can I find the nearest grocery store around here?",
        "She loves listening to jazz music while working on her laptop.",
        "We are organizing a hackathon for artificial intelligence projects.",
        "Have a great weekend and enjoy your time off!",
        "Learning a new language opens up doors to different cultures.",
        "The server responded with a status code of two hundred OK.",
        "Can you send me the link to the GitHub repository?",
        "It was a pleasure speaking with you earlier this afternoon.",
        "Let me know if you need any assistance with the installation.",
        "The project deadline has been moved to next Friday.",
        "Enjoy your meal and have a wonderful evening with your friends."
    ],
    "Hindi": [
        "नमस्ते, आपका स्वागत है! आप क्या लेना पसंद करेंगे?",
        "आज बहुत तेज धूप है और हवा भी गर्म लग रही है।",
        "कृपया मुझे बताएं कि इस सवाल का सही उत्तर क्या है?",
        "आपका बहुत-बहुत धन्यवाद, मुझे आपकी सहायता से बहुत लाभ हुआ।",
        "मुझे हिंदी भाषा में बातचीत करना बहुत अच्छा लगता है।",
        "हम सभी मिलकर इस समस्या का कोई अच्छा समाधान निकालेंगे।",
        "कल की परीक्षा की तैयारी के लिए मैं देर रात तक पढ़ रहा था।",
        "क्या आपके पास इस विषय से संबंधित कोई अच्छी पुस्तक है?",
        "सच्चे मित्र हमेशा सुख और दुख में साथ खड़े रहते हैं।",
        "सब्जी मंडी से ताजे फल और सब्जियां लेकर आना मत भूलना।",
        "आपकी यात्रा सुखद और सुरक्षित रहे, ऐसी मेरी ईश्वर से प्रार्थना है।",
        "यह गाना सुनकर मुझे अपने पुराने दिनों की याद आ गई।",
        "समय किसी की प्रतीक्षा नहीं करता, इसलिए हर पल मूल्यवान है।",
        "आज शाम को चाय के साथ समोसे खाने का मजा ही कुछ और है।",
        "शुभ रात्रि, आशा है कि कल का दिन आपके लिए मंगलमय होगा।"
    ],
    "Marathi": [
        "नमस्कार, तुमचे मनःपूर्वक स्वागत आहे! काय घेणार तुम्ही?",
        "आज खूपच छान गार वारा सुटला आहे आणि वातावरण आल्हाददायक आहे.",
        "कृपया मला सांगा की या प्रश्नाचे योग्य उत्तर काय असू शकते?",
        "तुमच्या बहुमूल्य सहकार्याबद्दल मनापासून खूप खूप धन्यवाद.",
        "मला मराठीतून संवाद साधायला आणि बोलायला खूप अभिमान वाटतो.",
        "आपण सर्व एकत्र येऊन या अडचणीवर नक्कीच मात करू शकतो.",
        "उद्याच्या परीक्षेचा सराव करण्यासाठी मी दिवसभर अभ्यास करत होतो.",
        "तुमच्याकडे या विषयावरील काही दर्जेदार पुस्तके उपलब्ध आहेत का?",
        "खरे मित्र संकटाच्या काळात कधीही पाठ फिरवत नाहीत, नेहमी सोबत असतात.",
        "बाजारातून ताजी भाजी आणि फळे घेऊन यायला विसरू नका.",
        "तुमचा प्रवास सुखकर आणि सुरक्षित होवो, हीच सदिच्छा.",
        "हे सुरेल गाणे ऐकून जुन्या गोड आठवणी ताज्या झाल्या.",
        "वेळ कोणासाठीही थांबत नाही, म्हणून वेळेचा सदुपयोग करा.",
        "संध्याकाळी गरमागरम कांदा भजी आणि चहा म्हणजे निखळ आनंद.",
        "शुभ रात्री, उद्याचा दिवस तुमच्यासाठी सुखसमृद्धीचा जावो."
    ],
    "French": [
        "Bonjour à tous! Comment se passe votre journée jusqu'ici?",
        "J'adore programmer en Python et développer des applications web modernes.",
        "Pourriez-vous me dire quelles sont les prévisions météorologiques pour demain?",
        "Merci beaucoup pour votre soutien précieux tout au long de ce projet.",
        "Où puis-je trouver une bonne boulangerie artisanale dans ce quartier?",
        "Elle écoute de la musique classique tout en écrivant sa thèse.",
        "Nous organisons un atelier consacré à l'intelligence artificielle appliquée.",
        "Passez un excellent week-end et profitez bien de votre temps libre!",
        "Apprendre une langue étrangère permet de mieux comprendre d'autres cultures.",
        "Le serveur a répondu rapidement avec un code deux cents sans aucune erreur.",
        "Pouvez-vous m'envoyer le lien vers le dépôt GitHub du projet?",
        "C'était un réel plaisir d'échanger avec vous cet après-midi.",
        "Faites-moi savoir si vous avez besoin d'aide pour la mise en route.",
        "La date limite de livraison a été reportée à vendredi prochain.",
        "Bon appétit et passez une agréable soirée en famille ou entre amis."
    ],
    "German": [
        "Guten Morgen allerseits! Wie läuft Ihr Arbeitstag bisher?",
        "Ich programmiere mit großer Begeisterung in Python und modernen Webtechnologien.",
        "Könnten Sie mir sagen, wie die Wettervorhersage für das Wochenende aussieht?",
        "Vielen herzlichen Dank für Ihre wertvolle Unterstützung bei dieser Aufgabe.",
        "Wo befindet sich hier in der Nähe der nächste Supermarkt?",
        "Sie hört gerne instrumentale Klaviermusik während der konzentrierten Arbeit.",
        "Wir organisieren einen ganztägigen Hackathon zum Thema Maschinelles Lernen.",
        "Schönes Wochenende und erholen Sie sich gut von der anstrengenden Woche!",
        "Das Erlernen einer neuen Sprache erweitert den geistigen Horizont enorm.",
        "Die Schnittstelle lieferte eine erfolgreiche Statusmeldung ohne Verzögerung.",
        "Könnten Sie mir bitte den Link zum GitHub-Repository weiterleiten?",
        "Es war mir eine große Freude, heute mit Ihnen zu sprechen.",
        "Geben Sie mir einfach Bescheid, falls Sie Hilfe bei der Installation benötigen.",
        "Die Abgabefrist für das Projekt wurde auf kommenden Freitag verschoben.",
        "Guten Appetit und einen wunderschönen, entspannten Abend im Kreise Ihrer Lieben."
    ],
    "Spanish": [
        "¡Buenos días a todos! ¿Cómo va su jornada hasta el momento?",
        "Me apasiona programar en Python, JavaScript y tecnologías de ciencia de datos.",
        "¿Podrías decirme qué pronóstico del tiempo tenemos para mañana?",
        "Muchísimas gracias por ayudarme a resolver este problema tan complejo.",
        "¿Dónde puedo encontrar un supermercado o tienda de abarrotes cerca de aquí?",
        "A ella le encanta escuchar música acústica mientras trabaja en su ordenador.",
        "Estamos organizando un hackatón enfocado en aplicaciones de inteligencia artificial.",
        "¡Que tengas un excelente fin de semana y disfrutes de tu descanso!",
        "Aprender un nuevo idioma te abre las puertas a fascinantes culturas del mundo.",
        "El servidor web respondió exitosamente con un código de estado doscientos.",
        "¿Serías tan amable de compartirme el enlace del repositorio en GitHub?",
        "Fue un verdadero placer conversar con usted durante la sesión de hoy.",
        "Avísame si necesitas cualquier tipo de orientación durante la configuración.",
        "La fecha límite de entrega se pospuso para el próximo viernes por la tarde.",
        "¡Buen provecho y que pases una velada inolvidable junto a tus seres queridos!"
    ],
    "Italian": [
        "Buongiorno a tutti! Come sta procedendo la vostra giornata finora?",
        "Mi piace moltissimo programmare in Python e costruire architetture dati scalabili.",
        "Potresti dirmi quali sono le previsioni del tempo per questo fine settimana?",
        "Grazie mille per avermi aiutato a trovare la soluzione a questo enigma.",
        "Scusi, dove posso trovare una buona farmacia o un negozio qui nei paraggi?",
        "Adora ascoltare brani jazz strumentali mentre scrive il suo nuovo articolo.",
        "Stiamo pianificando una giornata di studio dedicata alle reti neurali artificiali.",
        "Buon fine settimana e goditi un meritato riposo in totale tranquillità!",
        "Imparare una nuova lingua permette di entrare in empatia con popoli diversi.",
        "La risposta del server è arrivata immediatamente con codice di stato duecento.",
        "Potresti per cortesia inviarmi il collegamento al repository su GitHub?",
        "È stato davvero un piacere poter parlare e confrontarmi con te oggi.",
        "Fammi sapere qualora dovessi riscontrare qualunque problema con l'installazione.",
        "La scadenza per la consegna della documentazione è stata fissata a venerdì.",
        "Buon appetito e trascorri una piacevolissima serata in ottima compagnia."
    ],
    "Portuguese": [
        "Bom dia a todos! Como está sendo o dia de vocês até agora?",
        "Tenho grande paixão por programar em Python e construir sistemas inteligentes.",
        "Você saberia me informar qual é a previsão do tempo para os próximos dias?",
        "Muito obrigado por toda a colaboração e apoio que você me ofereceu hoje.",
        "Onde fica a padaria ou mercearia mais próxima aqui deste bairro?",
        "Ela gosta de trabalhar ouvindo músicas calmas e instrumentais nos fones.",
        "Estamos montando uma maratona de programação voltada para inovação e tecnologia.",
        "Tenha um excelente fim de semana e recarregue todas as suas energias!",
        "Dominar um novo idioma conecta você diretamente com pessoas de todo o planeta.",
        "A requisição ao servidor foi processada com sucesso retornando código duzentos.",
        "Poderia me mandar o link para acessar o código no repositório do GitHub?",
        "Foi uma enorme satisfação poder conversar e trocar ideias com você hoje.",
        "Fique à vontade para me procurar caso encontre dificuldades no processo de setup.",
        "O prazo final para submissão do trabalho acadêmico foi prorrogado para sexta.",
        "Bom apetite e tenha uma noite tranquila e descansada ao lado dos seus."
    ],
    "Russian": [
        "Всем доброе утро! Как проходит ваш сегодняшний рабочий день?",
        "Мне очень нравится программировать на языках Python, Go и TypeScript.",
        "Не подскажете, какой прогноз погоды передают синоптики на завтра?",
        "Огромное спасибо за вашу действенную помощь в решении этой сложной задачи.",
        "Подскажите, где поблизости находится ближайший продуктовый супермаркет?",
        "Она любит слушать приятную инструментальную музыку во время работы за компьютером.",
        "Мы готовимся к проведению хакатона по разработке моделей искусственного интеллекта.",
        "Желаю отличных выходных, хорошего отдыха и прекрасного восстановления сил!",
        "Изучение нового иностранного языка дарит возможность взглянуть на мир по-новому.",
        "Веб-сервер успешно обработал входящий запрос и вернул статус двести ОК.",
        "Могли бы вы отправить мне прямую ссылку на данный репозиторий в GitHub?",
        "Было очень приятно и продуктивно пообщаться с вами сегодня днем.",
        "Обязательно дайте знать, если вам потребуется помощь в установке библиотек.",
        "Крайний срок завершения этапа разработки был перенесен на следующую пятницу.",
        "Приятного аппетита и проведите замечательный, теплый вечер в кругу близких людей."
    ],
    "Arabic": [
        "صباح الخير جميعا! كيف تسير أموركم ومهامكم اليوم حتى الآن؟",
        "أستمتع كثيرا بالبرمجة بلغة بايثون وبناء تطبيقات تعلم الآلة المتقدمة.",
        "هل يمكنك إخباري كيف ستكون حالة الطقس المتوقعة ليوم غد؟",
        "شكرا جزيلا لك على مد يد العون والمساعدة في حل هذه المسألة الصعبة.",
        "أين يمكنني العثور على أقرب متجر للمواد الغذائية في هذا الحي؟",
        "تحب الاستماع إلى الموسيقى الهادئة أثناء القراءة والعمل على حاسوبها.",
        "نحن نعمل على تنظيم مسابقة برمجية في مجال الذكاء الاصطناعي التوليدي.",
        "أتمنى لك عطلة نهاية أسبوع سعيدة وممتعة تقضيها في راحة وهدوء تام!",
        "تعلم لغة جديدة يفتح أمامك آفاقا واسعة للتواصل مع مختلف الحضارات والشعوب.",
        "استجاب الخادم للطلب المرسل بنجاح تام مع رمز الحالة مئتين دون أي خطأ.",
        "هل يمكنك من فضلك إرسال الرابط الخاص بمستودع المشروع على منصة جيت هاب؟",
        "لقد كان من دواعي سروري التحدث معك وتبادل الأفكار الملهمة اليوم.",
        "يرجى إعلامي فورا إذا كنت بحاجة إلى أي مساعدة أثناء عملية التثبيت.",
        "تم تمديد الموعد النهائي لتسليم متطلبات المشروع إلى يوم الجمعة القادم.",
        "بالهناء والشفاء، وأتمنى لك قضاء أمسية ممتعة وسعيدة برفقة عائلتك الكريمة."
    ],
    "Chinese": [
        "大家早上好！请问各位今天的工作和学习进展得顺利吗？",
        "我非常热爱使用Python和主流前端框架开发实用高效的软件系统。",
        "你能帮我查一下气象部门对本周末天气情况的具体预测吗？",
        "非常感谢您悉心指导我攻克了这个困扰已久的技术难关。",
        "请问距离这里最近的大型生鲜超市或者便利店在哪个方向？",
        "在全神贯注撰写学术论文的时候，她喜欢戴上耳机听一些轻音乐。",
        "我们团队下个月计划组织一场面向青年开发者的人工智能极客马拉松。",
        "祝愿大家度过一个愉快充实、身心放松的周末美好时光！",
        "掌握一门全新的外语能让我们更深入地领略世界多元文化的魅力。",
        "后端服务器迅速响应了客户端请求，并返回了状态码二百成功标志。",
        "能否麻烦您把这个开源项目在GitHub上的仓库代码链接发给我一份？",
        "今天下午能有机会与您深入交流探讨，我感到非常荣幸与高兴。",
        "在后续的环境配置与服务部署过程中，如有任何疑问请随时与我联系。",
        "该项目第一阶段的交付截止日期已经统一部署顺延至下周五下午。",
        "祝您用餐愉快，愿您与家人朋友共度一个温馨宁静的美好夜晚。"
    ],
    "Japanese": [
        "皆さんおはようございます！本日の調子や進捗はいかがですか？",
        "私はPythonを用いた機械学習モデルの構築と開発がとても好きです。",
        "明日の天気予報や降水確率がどうなっているか教えていただけますか？",
        "この難しい技術的課題の解決に親身になってご協力いただき感謝いたします。",
        "すみません、この近所に品揃えの良いスーパーやコンビニはありますか？",
        "彼女はノートパソコンで執筆作業をしながら静かなピアノ曲を聴いています。",
        "私たちは来月、人工知能と自然言語処理をテーマにしたハッカソンを開催します。",
        "どうぞ充実した素晴らしい週末をお過ごしになり、日頃の疲れを癒やしてください！",
        "新しい外国語を学ぶことは、異なる文化や思考方法を理解する最高の窓口です。",
        "ウェブサーバーはリクエストを正常に受信し、ステータスコード二百を返しました。",
        "恐れ入りますが、GitHubのリポジトリへのリンクを共有していただけますでしょうか？",
        "本日のミーティングで皆様と有意義な意見交換ができたことを大変嬉しく思います。",
        "開発環境のセットアップや初期設定で不明な点がございましたら、いつでもご連絡ください。",
        "今回のプロジェクト開発フェーズの提出期限は来週金曜日まで延長されました。",
        "どうぞ美味しいお食事をお召し上がりいただき、ご家族と素敵な夜をお過ごしください。"
    ],
    "Korean": [
        "여러분 좋은 아침입니다! 오늘 하루도 활기차고 기분 좋게 시작하셨나요?",
        "저는 파이썬과 최신 웹 프레임워크를 활용하여 프로그램을 개발하는 것을 아주 좋아합니다.",
        "혹시 내일과 주말 동안의 날씨 예보가 어떻게 되는지 알려주실 수 있으신가요?",
        "이처럼 까다로운 알고리즘 문제를 해결하는 데 큰 도움을 주셔서 진심으로 감사드립니다.",
        "실례지만 이 근처에서 가장 가깝고 신선한 식료품을 파는 마트가 어디에 있나요?",
        "그녀는 컴퓨터 작업을 하면서 집중력을 높여주는 잔잔한 어쿠스틱 음악을 듣곤 합니다.",
        "저희 동아리에서는 다음 달에 인공지능과 빅데이터를 주제로 한 해커톤을 기획하고 있습니다.",
        "즐겁고 행복한 주말 보내시고, 그동안 쌓였던 피로를 말끔히 푸시기를 바랍니다!",
        "새로운 언어를 배우는 것은 다른 나라의 고유한 문화와 가치관을 이해하는 지름길입니다.",
        "웹 서버가 클라이언트 요청을 정상적으로 처리하여 상태 코드 이백을 반환했습니다.",
        "혹시 이번 프로젝트의 깃허브 저장소 링크를 저에게 메신저로 공유해 주실 수 있나요?",
        "오늘 오후에 여러분과 직접 만나 유익한 기술적 논의를 나눌 수 있어서 무척 기뻤습니다.",
        "설치나 라이브러리 환경 설정 과정에서 막히는 부분이 생기면 언제든 편하게 물어보세요.",
        "이번 스프린트의 최종 산출물 제출 기한이 다음 주 금요일까지로 공식 연장되었습니다.",
        "맛있는 저녁 식사 든든하게 드시고, 가족들과 함께 평안하고 따뜻한 밤 보내세요."
    ],
    "Dutch": [
        "Goedemorgen allemaal! Hoe verloopt jullie werkdag tot nu toe?",
        "Ik programmeer ontzettend graag in Python en bouw moderne webservices.",
        "Zou je mij kunnen vertellen wat het weerbericht voor komend weekend voorspelt?",
        "Hartelijk dank voor al je fantastische hulp bij het oplossen van dit probleem.",
        "Weet iemand waar ik hier in de buurt de dichtstbijzijnde supermarkt kan vinden?",
        "Zij luistert graag naar rustgevende akoestische muziek tijdens haar programmeerwerk.",
        "We organiseren een inspirerende hackathon gericht op innovaties in kunstmatige intelligentie.",
        "Fijn weekend gewenst en geniet lekker van je vrije tijd en de rust!",
        "Het leren van een vreemde taal verbreedt je kijk op de wereld en verbindt culturen.",
        "De server reageerde razendsnel en stuurde keurig een statuscode van tweehonderd terug.",
        "Zou je me de link naar het GitHub-project willen sturen via e-mail?",
        "Het was een waar genoegen om vanmiddag zo constructief met jou van gedachten te wisselen.",
        "Laat het me gerust even weten als je assistentie nodig hebt bij de installatie.",
        "De uiterste inleverdatum voor dit project is officieel verschoven naar volgende week vrijdag.",
        "Eet smakelijk en geniet van een hele gezellige en ontspannen avond met familie of vrienden."
    ],
    "Turkish": [
        "Herkese günaydın! Bugün gününüz nasıl başladı, işleriniz yolunda mı?",
        "Python ve modern web teknolojileri kullanarak yazılım geliştirmeyi çok seviyorum.",
        "Yarın için yapılan hava durumu tahminlerinin nasıl olduğunu bana söyleyebilir misiniz?",
        "Bu zorlu problemi çözmemde gösterdiğiniz değerli katkı ve destek için çok teşekkür ederim.",
        "Affedersiniz, bu civarda en yakın süpermarketi ya da bakkalı nerede bulabilirim?",
        "Bilgisayar başında kod yazarken kulaklıkla sakin enstrümantal müzikler dinlemeyi sever.",
        "Önümüzdeki ay yapay zekâ ve veri bilimi odaklı geniş katılımlı bir maraton düzenliyoruz.",
        "İyi hafta sonları dilerim, sevdiklerinizle birlikte güzelce dinlenip enerjinizi toplayın!",
        "Yeni bir dil öğrenmek, farklı kültürlerin zengin dünyasına yepyeni kapılar açar.",
        "Web sunucusu gelen isteği başarıyla yanıtlayarak iki yüz durum kodunu iletti.",
        "Rica etsem projenin GitHub üzerindeki kod deposunun bağlantısını bana gönderebilir misiniz?",
        "Bugün sizinle tanışmak ve bu önemli projeyi detaylıca değerlendirmek benim için büyük bir zevkti.",
        "Kurulum aşamasında ya da kütüphaneleri çalıştırırken bir sorunla karşılaşırsanız lütfen haber verin.",
        "Geliştirme sürecinin nihai teslim tarihi önümüzdeki cuma gününe kadar resmen ertelendi.",
        "Afiyet olsun, sevdiklerinizle beraber huzurlu, neşeli ve çok keyifli bir akşam geçirmenizi dilerim."
    ]
}

def append_additional_samples(file_path="data/language_dataset.csv"):
    existing_samples = set()
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_samples.add(row["text"].strip())
    
    new_rows = []
    for lang, sentences in ADDITIONAL_SAMPLES.items():
        for s in sentences:
            clean_s = s.strip()
            if clean_s and clean_s not in existing_samples:
                new_rows.append({"text": clean_s, "language": lang})
                
    with open(file_path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "language"])
        writer.writerows(new_rows)
        
    print(f"Added {len(new_rows)} extra high-quality samples. Total dataset expanded.")

if __name__ == "__main__":
    append_additional_samples()
