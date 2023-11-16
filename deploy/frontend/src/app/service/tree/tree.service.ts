import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class TreeService {
  constructor() {}

  convertStringDelimitedGroupToTree(data: string[], delimiter: string) {
    return data
      .sort((a, b) => a.localeCompare(b))
      .reduce((r, currentValue) => {
        const keys = currentValue.split(delimiter);

        const name = keys.pop();

        keys
          .reduce((t: any[], name) => {
            let temp: any = t.find(
              (o: any) => o.name === name && Array.isArray(o.children)
            );
            if (!temp) t.push((temp = { name, children: [] }));
            return temp.children;
          }, r)
          .push({ name, id: currentValue, children: [] });

        return r;
      }, []);
  }
}
