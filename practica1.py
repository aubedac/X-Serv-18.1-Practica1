#!/usr/bin/python

import webapp
import sys
import os.path
import urllib
import csv

class shortedUrl(webapp.webApp):

    def parse(self, request):
        method = request.split(' ', 2)[0]
        try:
            url = request.split(' ', 2)[1]
        except IndexError:
            url = ""
            body = ""
            urlSplited = ""

        try:
            body = urllib.unquote(request.split('\r\n\r\n')[1])
            body = body.split("=")[1]
            urlSplitted = body.split(":")
        except IndexError:
            body = ""
            urlSplitted = ""

        if len(urlSplitted) < 2:
            body = "http://" + body

        return (method, url, body)

    def process(self, parsedRequest):
        method, url, body = parsedRequest
        diccPrintable = ""

        if method == "GET":
            index = url.split('/',1)[1]
            if not self.shortUrls.has_key(index) and len(index) == 0:
                httpCode = '200 OK'
                header = ""
                for attribute, value in self.shortUrls.items():
                    diccPrintable += ('{} : {}'.format(attribute, value)+ "<br>\r\n") + "<br>\r\n"

                htmlBody = "<html><body>" + "<form method='POST' action="" >"  \
                            + "Introduce la URL que quieres acortar: " + '<input type="text" name=url">'  \
                            +  '<input type="submit" value="Enviar">'  \
                            + '</form>' + '<p>' + "Estado actual de el diccionario: " + '</p>' \
                            + '<p>' + diccPrintable + '</p>' \
                            + '</html></body>'

            elif int(index) <= int(self.assignamentNumber):
                url = self.shortUrls[str(index)]
                if url != "":
                    httpCode = '200 OK'
                    header = ""
                    htmlBody = "<html><body>" +"Existe una url para este rescurso: " + '<a href=' + url + '>' \
                                + url + '</a>'
                else:
                    httpCode = '404 Not Found'
                    header = ""
                    htmlBody = '<html><head><b>' + "404 Not Found"+ '</b></head><body>' + "<br>No existe el recurso solicitado" \
                                + '</body></html>'
                try:
                    source = index
                    if self.shortUrls.has_key(source):
                        redir = self.shortUrls[source]
                        httpCode = "302 Found"
                        header = "Location: " + redir
                        htmlBody = ""
                except ValueError:
                    pass

            else:
                httpCode = '400 Bad Request'
                htmlBody = '<html><head><b>' + "400 Bad Request"+ '</b></head><body>' + "<br>Recurso no valido." \
                            + '</body></html>'
                header = ""

        elif method == "POST":
            if body != "http://":
                if not self.urls.has_key(body):
                    httpCode = '200 OK'
                    header = ""
                    htmlBody =  '<html><body>' + "La url que quieres acortar es esta: " \
                                + '<a href=' + body + '>' + body + '</a>' \
                                + '<p> La url-corta asociada es:' + '<a href=http://localhost:1234/' + str(self.assignamentNumber) +'>' \
                                + "http://localhost:1234/" + str(self.assignamentNumber) + '</a></p>' \
                                + '</html></body>'

                    self.shortUrls[self.assignamentNumber] = body
                    self.urls[body] = self.assignamentNumber
                    self.assignamentNumber = int(self.assignamentNumber) + 1
                    with open ("directions.csv", "w") as fileCsv:
                        writer = csv.writer(fileCsv)
                        for key, value in self.shortUrls.items():
                            writer.writerow([key, value])

                else:
                    self.assignamentNumber = self.urls.get(body)
                    httpCode = '200 OK'
                    header = ""
                    htmlBody = '<html><body>' + "Ya me pediste acortar esta URL: " \
                                + '<p>' + '<a href=http://localhost:1234/' + str(self.assignamentNumber) +'>' \
                                + "http://localhost:1234/" + str(self.assignamentNumber) + '</a></p>' \
                                + '</html></body>'
            else:
                httpCode = "400 Bad Request"
                htmlBody = '<html><head><b>' + "400 Bad Request"+ '</b></head><body>' + "<br>Empty query String" + '</body></html>'
                header = ""

        else:
            httpCode = "405 Method Not Allowed"
            htmlBody = '<html><head><b>' + "405 Method Not Allowed"+ '</b></head><body>' + "<br>Solo GET o POST" + '</body></html>'
            header = ""

        return (httpCode, htmlBody, header)

    def __init__(self, hostname, port):
        self.assignamentNumber = 0
        self.urls = {}           # Key = URL | Value: shortedUrl
        self.shortUrls = {}      # Key = shortedUrl | Value = URL

        if not os.path.exists("directions.csv"):
            fileCsv = open("directions.csv","w")
            fileCsv.close()
        else:
            with open ("directions.csv", "r") as fileCsv:
                reader = csv.reader(fileCsv)
                for columns in reader:
                    try:
                        self.urls[columns[1]] = columns[0]
                        self.shortUrls[columns[0]] = columns[1]
                    except IndexError:
                        pass

                for index in self.shortUrls:
                    if self.assignamentNumber <= int(index):
                        self.assignamentNumber = int(index)
                        self.assignamentNumber = self.assignamentNumber + 1

        try:
            super(shortedUrl, self).__init__(hostname, port)
        except KeyboardInterrupt:
            with open ("directions.csv", "w") as fileCsv:
                writer = csv.writer(fileCsv)
                for key, value in self.shortUrls.items():
                    writer.writerow([key, value])

if __name__ == '__main__':
    shorted = shortedUrl("localhost",1234)
