LOOP_PROMPT = "Continue on your mission by using your tools"
SYSTEM_PROMPT = ""

class primary_agent:
    def __init__(self, name, wealth, preferences):
        self.prompt = name
        self.tools = []

    def take_action(self, options):
        #use the tools to take an action, basically there would be some standard prompt given to agent to keep going
        pass

    
        