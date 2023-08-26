import modal

stub = modal.Stub(name="example")


@stub.function(timeout=60 * 5)
@modal.web_endpoint(method="POST", label="example")
def example(body):
    print(body)
    return {"message": "Hello world!"}
