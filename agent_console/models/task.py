from agent_console import db
from agent_console.utils import setEmptySpacesLeading

class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(256), nullable=False, unique=True) # tehtävän nimi
    reward = db.Column(db.Integer, nullable=False) # palkintona rahaa
    code = db.Column(db.String(256), nullable=False, unique=True) # koodi, jolla suoritetaan
    done = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True) # kun pelaaja tehnyt, pelaajan id tähän
    description = db.Column(db.String(256), nullable=False) # ohjeet suoritukseen

    def __init__(self, name, reward, code, description):
        self.name = name.strip()
        self.reward = reward.strip()
        self.code = code.strip()
        self.description = description.strip()
        self.done = None

    def setId(self, id):
        response = "Tehtävän vanha id: " + str(self.id)
        self.id = int(id.strip())
        db.session.commit()
        response += ", uusi id: " + str(self.id)
        return response

    def setName(self, name):
        response = "Tehtävän vanha nimi: " + self.name
        self.name = name.strip()
        db.session.commit()
        response += ", uusi nimi: " + self.name
        return response
    
    def setReward(self, reward):
        response = "Tehtävän vanha palkinto: " + str(self.reward)
        self.reward = reward.strip()
        db.session.commit()
        response += ", uusi palkinto: " + str(self.reward)
        return response
    
    def setCode(self, code):
        response = "Tehtävän vanha koodi: " + self.code
        self.code = code.strip()
        db.session.commit()
        response += ", uusi koodi: " + self.code
        return response

    def setDescription(self, desc):
        response = "Tehtävän vanha kuvaus: " + self.description
        self.description = desc.strip()
        db.session.commit()
        response += ", uusi kuvaus: " + self.description
        return response
    
    def setClaim(self, userId):
        response = "Tehtävän vanha tekijä: " + str(self.done)
        self.done = userId.strip()
        db.session.commit()
        response += ", uusi tekijä: " + str(self.done)
        return response

    def unclaim(self):
        response = "Tehtävän vanha tekijä: " + str(self.done)
        self.done = ""
        db.session.commit()
        response += ", uusi tekijä: " + str(self.done)
        return response
    
    @staticmethod
    def getTask(taskId):
        return Task.query.filter_by(id=taskId).first()

    @staticmethod
    def listTasksForAdmin():
        tasks = Task.query.all()
        taskColumnSizes = [0] * 5
        taskColumnSizes[0] = 2
        taskColumnSizes[1] = 4
        taskColumnSizes[2] = 2
        taskColumnSizes[3] = 5
        taskColumnSizes[4] = 6
        for t in tasks:
            if len(str(t.id)) > taskColumnSizes[0]: taskColumnSizes[0] = len(str(t.id))
            if len(t.name) > taskColumnSizes[1]: taskColumnSizes[1] = len(t.name)
            if len(str(t.reward)) > taskColumnSizes[2]: taskColumnSizes[2] = len(str(t.reward))
            if len(t.code) > taskColumnSizes[3]: taskColumnSizes[3] = len(t.code)
            if len(str(t.done)) > taskColumnSizes[4]: taskColumnSizes[4] = len(str(t.done))

        response = setEmptySpacesLeading("id", taskColumnSizes[0]) + \
            " | " + setEmptySpacesLeading("nimi", taskColumnSizes[1]) + \
            " | " + setEmptySpacesLeading("$", taskColumnSizes[2]) + \
            " | " + setEmptySpacesLeading("koodi", taskColumnSizes[3]) + \
            " | " + setEmptySpacesLeading("tekijä", taskColumnSizes[4]) + \
            " | " + "kuvaus"
        
        for t in tasks:
            response += "\n" + setEmptySpacesLeading(str(t.id), taskColumnSizes[0]) + \
                        " | " + setEmptySpacesLeading(t.name, taskColumnSizes[1]) + \
                        " | " + setEmptySpacesLeading(str(t.reward), taskColumnSizes[2]) + \
                        " | " + setEmptySpacesLeading(t.code, taskColumnSizes[3]) + \
                        " | " + setEmptySpacesLeading(str(t.done), taskColumnSizes[4]) + \
                        " | " + t.description
        return response

    @staticmethod
    def listTasks():
        def sortByName(t):
            return t.name

        tasks = Task.query.filter_by().all()
        taskNameLength = 7
        taskRewardLength = 2

        for t in tasks:
            if taskNameLength < len(t.name): taskNameLength = len(t.name)
            if taskRewardLength < len(str(t.reward)): taskRewardLength = len(str(t.reward))

        tasks = Task.query.filter_by(done=None).all()
        tasks.sort(key=sortByName)

        response = setEmptySpacesLeading("tehtävä", taskNameLength) + " | " + setEmptySpacesLeading("$", taskRewardLength) + " | kuvaus"
        for t in tasks:
            response += "\n" + setEmptySpacesLeading(t.name, taskNameLength) + " | " + setEmptySpacesLeading(str(t.reward), taskRewardLength) + " | " + t.description

        tasks = Task.query.filter(Task.done != None).all()
        tasks.sort(key=sortByName)
        if len(tasks) > 0:
            response += "\n" + \
                        "\n" + "suoritetut tehtävät (ei voi suorittaa enää):"
            for t in tasks:
                response += "\n" + setEmptySpacesLeading(t.name, taskNameLength) + " | " + setEmptySpacesLeading(str(t.reward), taskRewardLength) + " | " + t.description

        return response
    
    @staticmethod
    def createTask(name,reward,code,description):
        db.session.add(Task(name,reward,code,description))
        db.session.commit()
        return "Tehtävä luotu: " + name + " | " + reward + " | " + code + " | " + description
    
    def delete(self):
        Task.query.filter_by(id=self.id).delete()
        db.session.commit()
        return "Tehtävä poistettu: " + str(self.id) + " | " + self.name + " | " + str(self.reward) + " | " + self.code + " | " + str(self.done) + " | " + self.description
