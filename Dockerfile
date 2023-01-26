FROM seedll/ubuntu_python

# runtime dependencies
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime; \
    set -eux; \
	apt-get update; \
    apt-get install -y --no-install-recommends \
    	software-properties-common ;\
    apt-add-repository ppa:mutlaqja/ppa -y; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
		git \
		indi-full \
		indi-bin \
		gsc \
		kstars-bleeding \
		; \
	rm -rf /var/lib/apt/lists/* ;\
	mkdir /app ; \
	cd /app ; \
	git clone https://github.com/AstroAir-Develop-Team/lightapt /app/lightapt ;\
	cd /app/lightapt; \
	pip install -r requirements.txt; \
	touch /app/Entrypoint.sh ; \
    echo "#!/bin/bash" >> /app/Entrypoint.sh ; \
	echo "cd /app/lightapt" >> /app/Entrypoint.sh ; \
	echo "python lightserver.py" >> /app/Entrypoint.sh

WORKDIR /app

EXPOSE 8000

CMD ["/usr/bin/bash", "/app/Entrypoint.sh"]
