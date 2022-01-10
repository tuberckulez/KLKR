#encoding "utf-8"

People -> AnyWord<kwtype="politiki">;  
Buildings -> AnyWord<kwtype="objects">;  

Data -> People interp (Data.People_output);
		
Data ->	Buildings interp (Data.Buildings_output);