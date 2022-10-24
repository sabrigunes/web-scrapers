class Data:
    project = 1
    ####### begin: PROJECT 1 #######
    datetime = None
    latitude = None
    longitude = None
    depth = None
    size_md = None
    size_ml = None
    size_mw = None
    location = None
    ####### end: PROJECT 1 #######


    def __init__(self, project):
        self.project = project

    def __str__(self):
        if self.project == 1:
            return f"{self.datetime}  {self.latitude}  {self.longitude}  {self.depth}  {self.size_md}  {self.size_ml}" \
                   f"  {self.size_mw}  {self.location}"




