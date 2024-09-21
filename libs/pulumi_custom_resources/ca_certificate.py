from os import remove


from pulumi.dynamic import CreateResult, Resource, ResourceProvider


class pulumi_new_ca_authority_provider(ResourceProvider):
    def create(self, inputs) -> CreateResult:
        with open(inputs["path"], "w") as file:
            file.write(inputs["content"])
        file.close()
        return CreateResult(id_=inputs["path"], outs=inputs)

    def delete(self, id, props) -> None:
        remove(id)


class pulumi_new_ca_authority_rsc(Resource):
    def __init__(
        self,
        name: str = None,
        content: str = None,
        path: str = None,
        opts=None,
    ) -> Resource:

        super().__init__(
            pulumi_new_ca_authority_provider(),
            name,
            {"content": content, "path": path},
            opts,
        )
