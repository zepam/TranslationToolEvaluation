# Notes on individual data preparation

## FCC

The original data is in paragraphs in PDF format. The data was copied to an excel spreadsheet and reviewed for accuracy, specifically to make sure the right to left langauges were copied correctly.

The paragraphs were split by sentence, so that each sentence was its own translation.

There were some translations that are inconsistent. This is often because one English sentence was separated into two translated sentences. Chinese (Traditional) and Chinese (Simplified) are affected due to parsing issues. This will be corrected.


The exceptions are listed here:

| file | row_index | issue | language | english_text | sentence_text |
| --- | ---: | --- | --- | --- | --- |
| 911 outage.csv | 1 | missing | Chinese (Traditional) | Please contact police, fire, medical, or other emergency services directly at their local phone numbers in case of emergency. | |
| 911 outage.csv | 2 | missing | Chinese (Simplified) | If you dial 9-1-1, you may not get help. | |
| 911 outage.csv | 2 | missing | Chinese (Traditional) | If you dial 9-1-1, you may not get help. | |
| Avalanche Warning.csv | 2 | missing | Chinese (Simplified) | LEAVE areas near [LOCATION]. | |
| Avalanche Warning.csv | 3 | missing | Chinese (Simplified) | DO NOT return to area after evacuation until directed by local officials. | |
| Avalanche Warning.csv | 3 | missing | Chinese (Traditional) | DO NOT return to area after evacuation until directed by local officials. | |
| Avalanche Warning.csv | 4 | missing | Chinese (Simplified) | Travel in the area is not recommended. | |
| Avalanche Warning.csv | 4 | missing | Chinese (Traditional) | Travel in the area is not recommended. | |
| Avalanche Warning.csv | 5 | missing | Chinese (Simplified) | Avalanches may run long distances. | |
| Avalanche Warning.csv | 5 | missing | Chinese (Traditional) | Avalanches may run long distances. | |
| Avalanche Warning.csv | 5 | missing | Russian | Avalanches may run long distances. | |
| Avalanche Warning.csv | 6 | extra | Arabic |  | لا تستخدم الثلج المصنوع من الماء الذي لم يتم غليه. |
| Avalanche Warning.csv | 7 | extra | Arabic |  | إذا كنت تستخدم تركيبة لإطعام طفلك، فاستخدم تركيبة جاهزة للاستخدام . |
| Avalanche Warning.csv | 8 | extra | Arabic |  | تأكد من عدم شرب الحيوانات الأليفة للماء الذي لم يتم غليه . |
| Boil Water Advisory.csv | 1 | missing | Chinese (Traditional) | Water in your community can make you sick. | |
| Boil Water Advisory.csv | 2 | missing | Chinese (Traditional) | Use bottled water if available. | |
| Boil Water Advisory.csv | 3 | missing | Chinese (Simplified) | Do not drink, cook with, brush your teeth with, or clean your home with tap water or filtered water until you boil it. | |
| Boil Water Advisory.csv | 3 | missing | Chinese (Traditional) | Do not drink, cook with, brush your teeth with, or clean your home with tap water or filtered water until you boil it. | |
| Boil Water Advisory.csv | 4 | missing | Chinese (Simplified) | Bring water to a full rolling boil for THREE MINUTES. | |
| Boil Water Advisory.csv | 4 | missing | Chinese (Traditional) | Bring water to a full rolling boil for THREE MINUTES. | |
| Boil Water Advisory.csv | 5 | missing | Chinese (Simplified) | Let water cool before use. | |
| Boil Water Advisory.csv | 5 | missing | Chinese (Traditional) | Let water cool before use. | |
| Boil Water Advisory.csv | 6 | missing | Chinese (Simplified) | Do not use ice made with water that has not been boiled. | |
| Boil Water Advisory.csv | 6 | missing | Chinese (Traditional) | Do not use ice made with water that has not been boiled. | |
| Boil Water Advisory.csv | 7 | missing | Chinese (Simplified) | If you use formula to feed your child, use ready-to-use formula. | |
| Boil Water Advisory.csv | 7 | missing | Chinese (Traditional) | If you use formula to feed your child, use ready-to-use formula. | |
| Boil Water Advisory.csv | 8 | missing | Chinese (Simplified) | Make sure pets do not drink water that has not been boiled. | |
| Boil Water Advisory.csv | 8 | missing | Chinese (Traditional) | Make sure pets do not drink water that has not been boiled. | |
| Boil Water Advisory.csv | 8 | missing | Haitian Creole | Make sure pets do not drink water that has not been boiled. | |
| Boil Water Advisory.csv | 8 | missing | Vietnamese | Make sure pets do not drink water that has not been boiled. | |
| Boil Water Advisory.csv | 9 | extra | Hindi |  | थिानीयमीतडयाजाुँिें। |
| Boil Water Advisory.csv | 9 | extra | Italian |  | Tenersi sempre aggiornati sui mezzi di comunicazione locali. |
| Boil Water Advisory.csv | 9 | extra | Spanish |  | Asegúrese de que sus mascotas no beban agua sin hervir. |
| Dust Storm Warning.csv | 1 | missing | Chinese (Simplified) | Be ready for sudden drop to zero visibility. | |
| Dust Storm Warning.csv | 1 | missing | Chinese (Traditional) | Be ready for sudden drop to zero visibility. | |
| Dust Storm Warning.csv | 2 | missing | Chinese (Simplified) | Pull Aside, Stay Alive! | |
| Dust Storm Warning.csv | 2 | missing | Chinese (Traditional) | Pull Aside, Stay Alive! | |
| Dust Storm Warning.csv | 3 | missing | Chinese (Simplified) | When visibility drops, pull far off the road and put your vehicle in park. | |
| Dust Storm Warning.csv | 3 | missing | Chinese (Traditional) | When visibility drops, pull far off the road and put your vehicle in park. | |
| Dust Storm Warning.csv | 4 | missing | Chinese (Simplified) | Turn the lights off and keep your foot off the brake. | |
| Dust Storm Warning.csv | 4 | missing | Chinese (Traditional) | Turn the lights off and keep your foot off the brake. | |
| Dust Storm Warning.csv | 5 | missing | Chinese (Simplified) | Infants, the elderly, and those with trouble breathing urged to take precautions. | |
| Dust Storm Warning.csv | 5 | missing | Chinese (Traditional) | Infants, the elderly, and those with trouble breathing urged to take precautions. | |
| Earthquake Warning.csv | 1 | missing | Chinese (Simplified) | Drop, Cover, Hold On. | |
| Earthquake Warning.csv | 1 | missing | Chinese (Traditional) | Drop, Cover, Hold On. | |
| Earthquake Warning.csv | 2 | missing | Chinese (Simplified) | Protect Yourself. | |
| Earthquake Warning.csv | 2 | missing | Chinese (Traditional) | Protect Yourself. | |
| Earthquake Warning.csv | 3 | missing | Chinese (Simplified) | [SENDING AGENCY] | |
| Earthquake Warning.csv | 3 | missing | Chinese (Traditional) | [SENDING AGENCY] | |
| Earthquake Warning.csv | 3 | missing | Portuguese | [SENDING AGENCY] | |
| Earthquake Warning.csv | 3 | missing | Spanish | [SENDING AGENCY] | |
| Earthquake Warning.csv | 3 | missing | Vietnamese | [SENDING AGENCY] | |
| Extreme Wind Warning.csv | 2 | missing | Chinese (Simplified) | Protect your head from flying objects. | |
| Extreme Wind Warning.csv | 3 | missing | Chinese (Simplified) | Do NOT go outside if the wind calms! | |
| Extreme Wind Warning.csv | 4 | missing | Chinese (Simplified) | Winds will quickly become dangerous again. | |
| Extreme Wind Warning.csv | 4 | missing | Chinese (Traditional) | Winds will quickly become dangerous again. | |
| Fire Warning.csv | 7 | missing | Haitian Creole | Watch for public safety personnel operating in the area and follow their instructions. | |
| Fire Warning.csv | 7 | missing | Italian | Watch for public safety personnel operating in the area and follow their instructions. | |
| Fire Warning.csv | 8 | extra | Vietnamese |  | Quan sát hoạt động của viên chức an toàn công cộng và làm theo hướng dẫn. |
| Severe Thunderstorm Warning.csv | 3 | extra | Vietnamese |  | Các vật thể bay có thể gây tử vong cho những ai ở bên ngoài nơi trú ẩn kiên cố. |
| Snow Squall Warning.csv | 2 | missing | Chinese (Simplified) | Be ready for a sudden drop to near zero visibility and icy roads in heavy snow. | |
| Snow Squall Warning.csv | 2 | missing | Chinese (Traditional) | Be ready for a sudden drop to near zero visibility and icy roads in heavy snow. | |
| Snow Squall Warning.csv | 2 | missing | Spanish | Be ready for a sudden drop to near zero visibility and icy roads in heavy snow. | |
| Snow Squall Warning.csv | 3 | extra | Russian |  | "Возможно резкое ухудшение видимости до нулевой, а также обледенение дорог из-за сильного снегопада." |
| Tornado Emergency.csv | 5 | missing | Korean | Check media. | |
| Tornado Emergency.csv | 6 | extra | Russian |  | Следите за новостями. |
| Tornado Warning.csv | 3 | missing | Korean | Check media. | |
| Tornado Warning.csv | 4 | extra | Russian |  | Следите за новостями. |
| Tornado Warning.csv | 4 | extra | Spanish |  | Si está al aire libre, en una casa rodante o vehículo, diríjase al edificio más cercano y resistente posible y protéjase de los escombros. |
| Tornado Warning.csv | 5 | extra | Spanish |  | Siga los medios de comunicación. |
| Tsunami Warning.csv | 5 | missing | Italian | Keep away from the coast until local officials say it is safe to return. | |
| Tsunami Warning.csv | 5 | missing | Russian | Keep away from the coast until local officials say it is safe to return. | |
| Tsunami Warning.csv | 5 | missing | Spanish | Keep away from the coast until local officials say it is safe to return. | |
