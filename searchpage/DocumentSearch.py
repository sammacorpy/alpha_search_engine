import os


class DocumentSearch:

    def __init__(self) -> None:
        super().__init__()

    def search(self, ext):
        file_name_location = ext+"Files.txt"
        currentdir = os.getcwd()
        text = ""
        ret = []
        for r, d, f in os.walk(currentdir):
            for file in f:
                if "."+ext in file:
                    text += os.path.join(r, file)+"\n"
                    ret.append(os.path.join(r, file))
        file = open(str(os.getcwd())+"/"+file_name_location, 'w')
        file.write(text)
        file.close()
        return ret
