from krules_core.base_functions import FilterFunction
import re


class IsSubscription(FilterFunction):

    def execute(self, subscription: int) -> bool:

        return self.payload["subscription"] == subscription


class GroupMatch(FilterFunction):

    def execute(
            self,
            group_regex: re.Pattern,
            groupdict_dest: [str | None] = None,
            groups_dest: [str | None] = None
    ) -> bool:

        match = group_regex.match(self.payload["group"])
        if match is not None:
            if groupdict_dest is not None:
                self.payload[groupdict_dest] = match.groupdict()
            if groups_dest is not None:
                self.payload[groups_dest] = match.groups()
            return True
        return False
