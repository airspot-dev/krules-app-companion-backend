import { TestBed } from '@angular/core/testing';

import { KrulesService } from './krules.service';

describe('KrulesService', () => {
  let service: KrulesService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(KrulesService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
