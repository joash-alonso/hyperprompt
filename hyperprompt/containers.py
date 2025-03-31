from pydantic import BaseModel, Field, model_validator

class PromptFragment(BaseModel):
    label: str
    variations: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_variations(self) -> 'PromptFragment':
        if not self.variations:
            raise ValueError("At least one variation must be provided")
        return self

class Prompt(BaseModel):
    prompt_fragments: list[PromptFragment]

    @property
    def labels(self) -> set[str]:
        return {fragment.label for fragment in self.prompt_fragments}

    @model_validator(mode='after')
    def validate_unique_labels(self) -> 'Prompt':
        if len(self.labels) != len(self.prompt_fragments):
            raise ValueError("All prompt fragment labels must be unique")
        return self

    @model_validator(mode='after')
    def validate_no_cycles(self) -> 'Prompt':
        # Build adjacency list representation of dependency graph
        graph = {fragment.label: fragment.dependencies for fragment in self.prompt_fragments}

        # Keep track of visited nodes and nodes in current path
        visited = set()
        path = set()

        def has_cycle(node: str) -> bool:
            if node in path:
                return True
            if node in visited:
                return False

            visited.add(node)
            path.add(node)

            # Check all dependencies for cycles
            for dependency in graph.get(node, []):
                if has_cycle(dependency):
                    return True

            path.remove(node)
            return False

        # Check each node for cycles
        for fragment in self.prompt_fragments:
            if has_cycle(fragment.label):
                raise ValueError("Cyclic dependencies detected in prompt fragments")

        return self

    @model_validator(mode='after')
    def validate_dependencies_exist(self) -> 'Prompt':
        # Get all available labels
        available_labels = self.labels

        # Check each fragment's dependencies
        for fragment in self.prompt_fragments:
            for dependency in fragment.dependencies:
                if dependency not in available_labels:
                    raise ValueError(f"Dependency '{dependency}' referenced in fragment '{fragment.label}' does not exist")

        return self


if __name__ == "__main__":  # pragma: no cover
    # Create some test prompt fragments
    fragment1 = PromptFragment(
        label="intro",
        variations=["Hello, my name is", 'Hi'],
        dependencies=[]
    )

    fragment2 = PromptFragment(
        label="name",
        variations=["Assistant"],
        dependencies=["intro"]
    )

    fragment3 = PromptFragment(
        label="role",
        variations=["I am here to help you."],
        dependencies=["name"]
    )

    # Create a prompt with the fragments
    prompt = Prompt(prompt_fragments=[fragment1, fragment2, fragment3])

    # Validate the prompt
    try:
        prompt = prompt.model_validate(prompt)
        print("Prompt validation successful!")
        print("Labels:", prompt.labels)
        print("Dependencies validated")
        print("No cycles detected")
    except ValueError as e:
        print(f"Validation failed: {e}")

