from datetime import datetime
from typing import Optional
from pydantic import BaseModel

silly_tavern_config = {
    "system_prompt":  "Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\nWrite {{char}}'s next reply in a fictional roleplay chat between {{user}} and {{char}}.\n",
    # system
    # wiBefore
    # description
    # personality
    # wiAfter
    # scenario
    # persona
    "story_string": "{{#if system}}{{system}}\n{{/if}}{{#if wiBefore}}{{wiBefore}}\n{{/if}}{{#if description}}{{description}}\n{{/if}}{{#if personality}}{{char}}'s personality: {{personality}}\n{{/if}}{{#if scenario}}Scenario: {{scenario}}\n{{/if}}{{#if wiAfter}}{{wiAfter}}\n{{/if}}{{#if persona}}{{persona}}\n{{/if}}",
}

class SillyTavernConfig(BaseModel):
    char_name: Optional[str]
    user_name: Optional[str]

    description: Optional[str] = ""
    personality: Optional[str] = ""
    scenario: Optional[str] = ""
    first_mes: Optional[str] = ""
    wiBefore: Optional[str] = ""
    wiAfter: Optional[str] = ""
    system_prompt:str = """Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\nWrite {{char}}'s next reply in a fictional roleplay chat between {{user}} and {{char}}.\n""",
    story_string:str ="""{{#if system}}{{system}}\n{{/if}}{{#if wiBefore}}{{wiBefore}}\n{{/if}}{{#if description}}{{description}}\n{{/if}}{{#if personality}}{{char}}'s personality: {{personality}}\n{{/if}}{{#if scenario}}Scenario: {{scenario}}\n{{/if}}{{#if wiAfter}}{{wiAfter}}\n{{/if}}{{#if persona}}{{persona}}\n{{/if}}"""

    def __init__(self,char_name:str,user_name:str,description:Optional[str] = "",scenario:Optional[str] = "",personality:Optional[str] = ""):
        super().__init__(char_name=char_name, user_name=user_name, description=description, scenario=scenario, personality=personality)

    def get_prompt(self):
        story = self.story_string
        # Replace other placeholders
        replacements = {
            "{{#if system}}{{system}}":  self.system_prompt[0] or "",
            "{{#if wiBefore}}{{wiBefore}}": self.wiBefore or "",
            "{{#if wiAfter}}{{wiAfter}}": self.wiAfter or "",
            "{{#if description}}{{description}}": self.description or "",
            "{{#if personality}}": "",
            "{{personality}}": self.personality or "",
            "{{#if scenario}}":"",
            "{{scenario}}": self.scenario or "",
            "{{#if persona}}": "",
            "{{persona}}": "",
            # "{{user}}": self.user_name,
            "{{char}}": self.char_name
        }

        for placeholder, value in replacements.items():
            if isinstance(value, str):  # Ensure value is a string
                story = story.replace(placeholder, value)

        # Remove remaining if tags
        story = story.replace("{{#if}}", "").replace("{{/if}}", "")

        return {
            "personality": self.personality,
            "scenario": self.scenario,
            "description": self.description,
            "story_string": story
        }


desc = """人物註解：
姓名：單曉曉
其他名稱：前江東市書記
年齡：18
性別：女

服裝：
-輕便女裝碎花裙。


身體:
-頭髮：黑色，長髮，及肩，眼睛：紅色，大，身高：168cm，稍小，體重：52kg，體型：普通，胸圍：平胸，80cm，腰圍：53cm，臀圍：89cm , 皮膚: 白色, 蒼白
- 柔弱有女人味的外表。

演講風格：
-強勢的聲音

外在性格：
- 傲娇的少女，性格極度惡劣。

內在個性：
-享受權力的人，看不起比自己地位低的人，為了權力會付出所有。

價值觀：
-相信自己是能掌握江東市無上權力的人。

目標：
-重奪江東市的控制權。
"""

def get_demo_character():
    # character = CharactersModel()
    # config = SillyTavernConfig(**character)

    config = SillyTavernConfig("huahua", "laios", desc)
    promptRes = config.get_prompt()
    print(promptRes["story_string"])
    return promptRes


class CharactersModel(BaseModel):
    id: str
    name: str
    uid: Optional[str] = "1"
    avatar: Optional[str] = ""

    # 猫箱
    prologue: Optional[str] = ""
    introduction: Optional[str] = ""
    settings: Optional[str] = ""
    style: Optional[str] = ""

    # silly
    description: Optional[str] = ""
    personality: Optional[str] = ""
    scenario: Optional[str] = ""

    prompt: Optional[str] = ""
    llm: Optional[str] = "openai"
    token_id: Optional[str] = ""

    public: bool = False
    created_at: datetime = datetime.now()


