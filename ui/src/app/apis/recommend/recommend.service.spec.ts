import { TestBed } from '@angular/core/testing';

import { RecommendsService } from './recommend.service';

describe('RecommendsService', () => {
  let service: RecommendsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(RecommendsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
