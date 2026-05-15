target = duckwing

.build: Dockerfile
	docker build -t $(target) .
	touch .build


local: .build static/helice_lowpoly.stl
	docker run \
		-v ${PWD}:/mnt/ \
		-p 127.0.0.1:8002:8002 \
		-w /mnt/ \
		-it --rm $(target) \
		fastapi dev --port=8002 --host=0.0.0.0

# N.B. jupyter notebook with build123d should be launched outside docker b/c
# hard to install in docker
# I think I used the python version in conda!? "conda activate ___ ?"
# This was very frustrating at the time, and now I can't remember how I did it

bash: .build
	docker run \
		-v ${PWD}:/mnt/ \
		-w /mnt/ \
		-it --rm $(target) \
		bash

jupyter: .build
	docker run \
		-v ${PWD}:/mnt/ \
		-p 127.0.0.1:8003:8003 \
		-w /mnt/ \
		-it --rm $(target) \
		jupyter lab --port=8003 --ip 0.0.0.0


clean:
	rm .build


tacking.gif: .build render.py
	docker run \
		-v ${PWD}:/mnt/ \
		-w /mnt/ \
		-it --rm $(target) \
		micromamba run python -c 'import render; render.write_tacking_animation()'

hoist.gif: .build render.py
	docker run \
		-v ${PWD}:/mnt/ \
		-w /mnt/ \
		-it --rm $(target) \
		micromamba run python -c 'import render; render.write_hoist_animation()'
