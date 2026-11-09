1. install docker
2. run: uv run .\paper\build_paper.py
3. docker run --rm `                                                                                                  
    -v "${PWD}/paper:/data" `
    -e JOURNAL=joss `
    openjournals/inara
4. paper.pdf gets generated