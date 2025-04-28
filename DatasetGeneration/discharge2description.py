import os
import shutil
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from textwrap import dedent
from pydantic import BaseModel
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
oak = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = oak

# 定义输入数据
input_data = """
 
Name:  ___               Unit No:   ___
 
Admission Date:  ___              Discharge Date:   ___
 
Date of Birth:  ___             Sex:   F
 
Service: SURGERY
 
Allergies: 
Tetracycline Analogues / amoxicillin / iodopropynl / 
glutaraldehyde
 
Attending: ___.
 
Chief Complaint:
Morbid obesity
 
Major Surgical or Invasive Procedure:
___: laparoscopic sleeve gastrectomy

 
History of Present Illness:
Per Dr. ___ has class III morbid obesity with 
weight of 286.9 pounds as of ___ with her initial screen 
weight of 285.1 pounds on ___, height of 63.25 inches and BMI 
of 50.4.  Her previous weight loss efforts have included Weight 
Watchers multiple times, calorie counting, low carbohydrate diet 
___, ___ diet, prescription weight loss 
medications, over-the-counter dietary ___ visits 
as well as counseling with obesity specialist Dr. ___ 
___ at ___.  She stated 
that her lowest weight was in the 180s in her teenage years and 
her highest weight was 297 pounds. She stated that she has been 
struggling with weight since puberty and cites as factors 
contributing to her excess weight convenience eating, lack 
portions, emotional eating ___ times a
month, genetics, eating too many carbohydrates and lack of 
exercise although she does walk for 60 minutes ___ times per 
week and does track her progress via a pedometer.  She denied 
history of eating disorders - no anorexia, bulimia, diuretic or 
laxative abuse and she denied binge eating.  She does not have a 
diagnosis of depression but does have anxiety with history of 
panic
attacks.  She has not been followed by a therapist and she has
not been hospitalized for mental health issues and she is not on
any psychotropic medications.

 
Past Medical History:
Her medical history includes:

1)  hyperlipidemia with elevated triglycerides
2)  hypertension not a medication
3)  vitamin D deficiency
4)  iron deficiency with saturation of 16%
5)  acne
6)  eczema
7)  ___ fracture of the right foot (inversion plantar flexion 
    after tripping down stairs at ___ at a ___)

She has no surgical history.

 
Social History:
Works as ___ at ___.

 
Physical Exam:
VS: T 98.3 P 76 BP 135/81 RR 18 02 100%RA
Constitutional: NAD
Neuro: Alert and oriented x 3
Cardiac: Regular rate and rhythm, no murmurs appreciated
Resp: Clear to auscultation, bilaterally
Abdomen: Soft, non-tender, non-distended, no rebound 
tenderness/guarding
Wounds: Abd lap sites, CDI; no periwound erythema or drainage
Ext: no lower extremity edema
 
Pertinent Results:
LABS:
___ 05:50AM BLOOD Hct-39.8
___ 10:32AM BLOOD Hct-40.4

IMAGING:
BAS/UGI W/KUB: 
No evidence of leak or obstruction.
 
Brief Hospital Course:
The patient presented to pre-op on ___. Pt was 
evaluated by anaesthesia and taken to the operating room for 
laparoscopic sleeve gastrectomy. There were no adverse events in 
the operating room; please see the operative note for details. 
Pt was extubated, taken to the PACU until stable, then 
transferred to the ward for observation. 

Neuro: The patient was alert and oriented throughout 
hospitalization; pain was initially managed with a PCA and then 
transitioned to oral oxycodone once tolerating a stage 2 diet. 
CV: The patient remained stable from a cardiovascular 
standpoint; vital signs were routinely monitored.
Pulmonary: The patient remained stable from a pulmonary 
standpoint; vital signs were routinely monitored. Good pulmonary 
toilet, early ambulation and incentive spirometry were 
encouraged throughout hospitalization. 
GI/GU/FEN: The patient was initially kept NPO with a 
___ tube in place for decompression.  On POD1, the NGT 
was removed and an upper GI study was negative for a leak, 
therefore, the diet was advanced sequentially to a Bariatric 
Stage 3 diet, which was well tolerated. Patient's intake and 
output were closely monitored.  
ID: The patient's fever curves were closely watched for signs of 
infection, of which there were none.
HEME: The patient's blood counts were closely watched for signs 
of bleeding, of which there were none.
Prophylaxis: The patient received subcutaneous heparin and ___ 
dyne boots were used during this stay and was encouraged to get 
up and ambulate as early as possible.

At the time of discharge, the patient was doing well, afebrile 
with stable vital signs.  The patient was tolerating a stage 3 
diet, ambulating, voiding without assistance, and pain was well 
controlled.  The patient received discharge teaching and 
follow-up instructions with understanding verbalized and 
agreement with the discharge plan.

 
Medications on Admission:
The Preadmission Medication list may be inaccurate and requires 
futher investigation.
1. levonorgestrel 20 mcg/24 hr ___ years) intrauterine DAILY 
2. Spironolactone 50 mg PO QHS 
3. Multivitamins W/minerals 1 TAB PO DAILY 
4. Imipramine 50 mg PO AS DIRECTED 

 
Discharge Medications:
1.  Docusate Sodium 100 mg PO BID:PRN constipation 
RX *docusate sodium 50 mg/5 mL 10 ml by mouth twice a day 
Refills:*0 
2.  OxycoDONE Liquid 5 mg PO Q6H:PRN Pain - Moderate 
RX *oxycodone 5 mg/5 mL 5 ml by mouth q 6 hours Refills:*0 
3.  Ranitidine (Liquid) 150 mg PO BID 
RX *ranitidine HCl 15 mg/mL 10 ml by mouth twice a day 
Refills:*0 
4.  Imipramine 50 mg PO AS DIRECTED  
5.  levonorgestrel 20 mcg/24 hr ___ years) intrauterine DAILY  
6.  Multivitamins W/minerals 1 TAB PO DAILY  
7. HELD- Spironolactone 50 mg PO QHS  This medication was held. 
Do not restart Spironolactone until you discuss with Dr. ___.

 
Discharge Disposition:
Home
 
Discharge Diagnosis:
Obesity

 
Discharge Condition:
Mental Status: Clear and coherent.
Level of Consciousness: Alert and interactive.
Activity Status: Ambulatory - Independent.

 
Discharge Instructions:
Discharge Instructions: Please call your surgeon or return to 
the emergency department if you develop a fever greater than 
101.5, chest pain, shortness of breath, severe abdominal pain, 
pain unrelieved by your pain medication, severe nausea or 
vomiting, severe abdominal bloating, inability to eat or drink, 
foul smelling or colorful drainage from your incisions, redness 
or swelling around your incisions, or any other symptoms which 
are concerning to you.

Diet: Stay on Stage III diet until your follow up appointment. 
Do not self advance diet, do not drink out of a straw or chew 
gum.

Medication Instructions:
Resume your home medications, CRUSH ALL PILLS.
You will be starting some new medications:
1.  You are being discharged on medications to treat the pain 
from your operation. These medications will make you drowsy and 
impair your ability to drive a motor vehicle or operate 
machinery safely. You MUST refrain from such activities while 
taking these medications.
2. You should begin taking a chewable complete multivitamin with 
minerals. No gummy vitamins.
3. You will be taking Zantac liquid ___ mg twice daily for one 
month. This medicine prevents gastric reflux.
4. You should take a stool softener, Colace, twice daily for 
constipation as needed, or until you resume a normal bowel 
pattern.
5. You must not use NSAIDS (non-steroidal anti-inflammatory 
drugs) Examples are Ibuprofen, Motrin, Aleve, Nuprin and 
Naproxen. These agents will cause bleeding and ulcers in your 
digestive system.

Activity:
No heavy lifting of items ___ pounds for 6 weeks. You may 
resume moderate exercise at your discretion, no abdominal 
exercises.

Wound Care:
You may shower, no tub baths or swimming. 
If there is clear drainage from your incisions, cover with 
clean, dry gauze. 
Your steri-strips will fall off on their own. Please remove any 
remaining strips ___ days after surgery.
Please call the doctor if you have increased pain, swelling, 
redness, or drainage from the incision sites. 
"""

# 定义输出数据模型
class PatientDescription(BaseModel):
    BasicInformation: dict
    OtherInformation: dict
    Symptoms: list[str]

@CrewBase
class Patient_Description_Crew():
    @agent
    def data_cleaner(self) -> Agent:
        """Agent 用于提取医疗记录中的基本信息和症状"""
        return Agent(
            config=self.agents_config['data_cleaner'],
            verbose=True
        )
    
    @task
    def extract_patient_info_task(self) -> Task:
        """Task 用于生成患者信息提取结果"""
        return Task(
            config=self.tasks_config['extract_patient_info_task'],
            output_pydantic=PatientDescription,
            output_file="output/patient_description.json",
        )

    @crew
    def crew(self) -> Crew:
        """创建用于提取患者信息的 Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

def run():
    # 输入医疗记录文本
    inputs = {
        'text': input_data
    }

    # 执行 Crew
    result = Patient_Description_Crew().crew().kickoff(inputs=inputs)

    print("\n\n=== FINAL REPORT ===\n\n")
    print(result.raw)

    print("Over.")

    # 提取患者姓名
    patient_name = result.pydantic.BasicInformation.get("Name", "Unknown")
    if patient_name:
        file_name = f"{patient_name}_patient_description.json"
    else:
        file_name = "patient_description.json"
    
    # 保存结果到指定文件夹
    source_file = 'output/patient_description.json'
    target_path = os.path.join('patient_descriptions', file_name)
    os.makedirs('patient_descriptions', exist_ok=True)
    shutil.copy2(source_file, target_path)
    print(f"\n\nReport has been saved to patient_descriptions/{file_name}")


if __name__ == "__main__":
    run()