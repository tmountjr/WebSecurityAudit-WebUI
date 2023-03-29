FROM golang:1.20-bullseye

WORKDIR /wsra
COPY app/ ./

# Update python dependencies
RUN apt update && apt upgrade -y
RUN apt install -y python3-setuptools
RUN apt install -y python3-pip

# Install httpx and subfinder
RUN go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# Install wafw00f
RUN git clone https://github.com/EnableSecurity/wafw00f.git
WORKDIR /wsra/wafw00f
RUN python3 setup.py install

# Install Python requirements
WORKDIR /wsra
RUN pip3 install -r requirements.txt

ARG PORT=5000
ENV PORT=$PORT
EXPOSE $PORT

ENTRYPOINT [ "python3" ]

CMD [ "WebSecurityAudit.py" ]