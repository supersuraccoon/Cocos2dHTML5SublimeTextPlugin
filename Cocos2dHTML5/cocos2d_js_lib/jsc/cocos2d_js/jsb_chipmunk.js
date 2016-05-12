//
// Chipmunk defines
//

var cp = cp || {};

cp.v = cc.p;
cp._v = cc._p;
cp.vzero  = cp.v(0,0);

// Vector: Compatibility with Chipmunk-JS
cp.v.add = cp.vadd;
cp.v.clamp = cp.vclamp;
cp.v.cross = cp.vcross;
cp.v.dist = cp.vdist;
cp.v.distsq = cp.vdistsq;
cp.v.dot = cp.vdot;
cp.v.eql = cp.veql;
cp.v.forangle = cp.vforangle;
cp.v.len = cp.vlength;
cp.v.lengthsq = cp.vlengthsq;
cp.v.lerp = cp.vlerp;
cp.v.lerpconst = cp.vlerpconst;
cp.v.mult = cp.vmult;
cp.v.near = cp.vnear;
cp.v.neg = cp.vneg;
cp.v.normalize = cp.vnormalize;
cp.v.normalize_safe = cp.vnormalize_safe;
cp.v.perp = cp.vperp;
cp.v.project = cp.vproject;
cp.v.rotate = cp.vrotate;
cp.v.rperp = cp.vrperp;
cp.v.slerp = cp.vslerp;
cp.v.slerpconst = cp.vslerpconst;
cp.v.sub = cp.vsub;
cp.v.toangle = cp.vtoangle;
cp.v.unrotate = cp.vunrotate;

// XXX: renaming functions should be supported in JSB
cp.clamp01 = cp.fclamp01;


/// Initialize an offset box shaped polygon shape.
cp.BoxShape2 = function(body, box)
{
	var verts = [
		box.l, box.b,
		box.l, box.t,
		box.r, box.t,
		box.r, box.b
	];

	return new cp.PolyShape(body, verts, cp.vzero);
};

/// Initialize a box shaped polygon shape.
cp.BoxShape = function(body, width, height)
{
	var hw = width/2;
	var hh = height/2;

	return cp.BoxShape2(body, new cp.BB(-hw, -hh, hw, hh));
};


/// Initialize an static body
cp.StaticBody = function()
{
	return new cp.Body(Infinity, Infinity);
};


// "Bounding Box" compatibility with Chipmunk-JS
cp.BB = function(l, b, r, t)
{
	return {l:l, b:b, r:r, t:t};
};

// helper function to create a BB
cp.bb = function(l, b, r, t) {
	return new cp.BB(l, b, r, t);
};

//
// Some properties
//
// "handle" needed in some cases
