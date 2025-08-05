import os
import re
import sys
import tempfile
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from fastapi.params import Depends
from whoosh import scoring
from whoosh.fields import Schema, ID, TEXT, NGRAM
from whoosh.index import create_in, FileIndex
from whoosh.qparser import QueryParser
import requests

SOURCE = os.environ.get("CRS_SOURCE", 'crs-list.txt')


def build_search_index():
    index_dir = tempfile.mkdtemp()
    schema = Schema(uri=NGRAM(minsize=2, maxsize=6, stored=True))
    idx = create_in(index_dir, schema)
    writer = idx.writer()

    print(f'Loading source from {SOURCE}...', end='', file=sys.stderr, flush=True)
    if re.match(r'^https?://.*', SOURCE):
        r = requests.get(SOURCE, stream=True)
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if not line.startswith('#'):
                writer.add_document(uri=line.strip().replace('https://www.opengis.net/def/crs/', ''))
    else:
        with open(SOURCE) as f:
            for line in f:
                if not line.startswith('#'):
                    writer.add_document(uri=line.strip().replace('https://www.opengis.net/def/crs/', ''))
    writer.commit()
    print(' [ok]', file=sys.stderr, flush=True)
    return idx


async def get_search_index() -> FileIndex:
    return app.state.idx


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    app.state.idx = build_search_index()
    yield


app = FastAPI(lifespan=app_lifespan)


@app.get('/search')
def search(q: str = Query(..., min_length=1), idx: FileIndex = Depends(get_search_index)):
    q = re.sub(r'[^A-Za-z0-9_/.,-]', '', q)
    results = []
    with idx.searcher(weighting=scoring.Frequency) as searcher:
        query = QueryParser("uri", idx.schema).parse(q)
        raw_results = searcher.search(query, limit=20)

        # Prioritize prefix matches
        for hit in raw_results:
            uri = hit["uri"]
            score = hit.score
            if uri.startswith(q):
                score += 10  # Boost prefix matches
            if not re.match(r'^https?://.*', uri):
                uri = f'https://www.opengis.net/def/crs/{uri}'
            results.append({"uri": uri, "score": score})

        # Sort by boosted score
        results.sort(key=lambda x: -x["score"])

    return {"query": q, "results": results}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False, lifespan="on")
