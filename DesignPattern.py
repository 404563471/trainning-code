from abc import ABCMeta, abstractmethod


class student():
    __slots__ = ("name", "_score", "__grade")

    def __init__(self, name, _score):
        self.name = name
        self.score = _score
        self.__grade = self.grade()

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        if not isinstance(value, int):
            raise ValueError('score must be an integer!')
        if value < 0 or value > 100:
            raise ValueError('score must between 0 ~ 100!')
        self._score = value

    @abstractmethod
    def grade(self):
        pass

    def get_grade(self):
        return self.__grade


class normalStudent(student):
    def grade(self):
        if self._score >= 90:
            value = "A"
        elif self.score < 60:
            value = "C"
        else:
            value = "B"
        return value


class someStudent(student):
    def grade(self):
        if self._score >= 90:
            value = "A"
        elif self.score < 60 ** 0.5:
            value = "C"
        else:
            value = "B"
        return value


class teacher():
    def __init__(self, grade):
        self.grade = grade
        self.__gradeComment = self.setComment()

    @abstractmethod
    def setComment(self):
        pass

    def getComment(self):
        return self.__gradeComment


class niceTeacher(teacher):
    def setComment(self):
        if self.grade == "A":
            self._gradeComment = "Good job!"
        elif self.grade == "B":
            self._gradeComment = "Not so bad!"
        elif self.grade == "C":
            self._gradeComment = "Do you want talk?"
        else:
            raise ValueError("grade mast be 'A', 'B', 'C'")
        return self._gradeComment


class strictTeacher(teacher):
    def setComment(self):
        if self.grade == "A":
            self._gradeComment = "Not so bad!"
        elif self.grade == "B":
            self._gradeComment = "Close to failing."
        elif self.grade == "C":
            self._gradeComment = "See you next year."
        else:
            raise ValueError("grade mast be 'A', 'B', 'C'")
        return self._gradeComment

class mathGrade(someStudent, niceTeacher):
    def __init__(self, name, _score):
        someStudent.__init__(self, name, _score)
        niceTeacher.__init__(self, self.get_grade())