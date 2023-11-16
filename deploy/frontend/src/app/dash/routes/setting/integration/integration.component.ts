import { Component } from '@angular/core';
import { integrations } from 'src/app/mock/integrations';
import { IIntegration } from 'src/app/models/intergration';

@Component({
  selector: 'app-integration',
  templateUrl: './integration.component.html',
  styleUrls: ['./integration.component.scss'],
})
export class IntegrationComponent {
  integrations: IIntegration[] = integrations;
  constructor() {}
}
