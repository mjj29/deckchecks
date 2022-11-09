import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PairingsComponent } from './pairings.component';

describe('PairingsComponent', () => {
	  let component: PairingsComponent;
	  let fixture: ComponentFixture<PairingsComponent>;

	  beforeEach(async(() => {
		      TestBed.configureTestingModule({
					      declarations: [ PairingsComponent ]
					    })
		      .compileComponents();
		    }));

	  beforeEach(() => {
		      fixture = TestBed.createComponent(PairingsComponent);
		      component = fixture.componentInstance;
		      fixture.detectChanges();
		    });

	  it('should create', () => {
		      expect(component).toBeTruthy();
		    });
});

