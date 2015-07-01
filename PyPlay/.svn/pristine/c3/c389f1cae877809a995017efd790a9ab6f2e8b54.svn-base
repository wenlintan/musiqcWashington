import math
from vector3 import *

import pygame
from pygame.locals import *

import material
from shapes import ray, collision

class voxel:
    def __init__( self, mat = None ):
        self.mat = mat

class voxel_tree:
    
    mask_block_dim = 4
    mask_block_dim_sq = mask_block_dim ** 2
    mask_block_dim_cu = mask_block_dim ** 3
    mask_dim = vector3( mask_block_dim, mask_block_dim, mask_block_dim )

    voxel_world_size = 0.1
    
    def __init__( self, pos, dim ):
        self.pos = pos
        self.dim = dim

        self.block_dim = self.dim / voxel_tree.mask_block_dim
        self.block_dim /= voxel_tree.voxel_world_size
        
        self.mask = [0L] * int(self.block_dim.x * self.block_dim.y * self.block_dim.z)
        #self.voxels = [0] * int(dim.x * dim.y * dim.z) * voxel_tree.mask_block_dim ** 3
    
    def collide( self, ray ):
        
        coll = collision( ray )
        ray_d = ray.d

        start = ray.s - self.pos
        if not self.dim.contains( start ):
            
            #compute distance ray must travel in each direction and divide by speed in that dir
            minbounds = -start
            maxbounds = -start + vector3( self.dim.x, self.dim.y, self.dim.z )

            t = minbounds.component_div(ray_d).raw_list
            t.extend( maxbounds.component_div(ray_d).raw_list )
            
            #cut out all t values behind start point and that aren't actually in voxel space
            t = [ i for i in t if i > 0.0 ]
            t = [ i for i in t if self.dim.contains( ray.s + ray_d * i ) ]
            if not len(t):   return coll()

            # take closest t value
            t.sort()
            t = t.pop()
            start = ray.s + ray_d * t
        
        diff = start - self.pos
        mask = self._create_mask( ray.d )
        
        #scale d so direction of maximum increase increases in steps of mask_block_dim
        m = max( enumerate( ray.d.raw ) , key = lambda t: t.__getitem__(1) )
        scale = voxel_tree.mask_block_dim / m[ 1 ]
        d = ray_d * scale

        #create pos as integer coordinate in mask, dp as sub position
        p = diff / voxel_tree.voxel_world_size / voxel_tree.mask_block_dim
        pos = vector3( int(p.x), int(p.y), int(p.z) )
        dp = ( pos - p ) * voxel_tree.mask_block_dim
        
        while self.dim.contains( pos ):
            #find the shift for the ray's mask and the mask-block that we're at
            mask_shift = int(dp.x + dp.y * voxel_tree.mask_block_dim + dp.z * voxel_tree.mask_block_dim_sq )
            mask_pos = int(pos.x + pos.y * voxel_tree.dim.x + pos.z * voxel_tree.dim.x * voxel_tree.dim.y )

            #find the actual two masks
            ray_mask = mask >> mask_shift
            geo_mask = self.mask[ mask_pos ]

            #if there is any overlap, there is a collision here
            if ray_mask & geo_mask:
                overlap = ray_mask & geo_mask

                p = 0
                while overlap:
                    p += 1
                    overlap = overlap >> 1

                z = p / voxel_tree.mask_block_dim_sq
                y = (p - z*voxel_tree.mask_block_dim_sq) / voxel_tree.mask_block_dim
                x = (p - z*voxel_tree.mask_block_dim_sq - y*voxel_tree.mask_block_dim) / voxel_tree.mask_block_dim

                hit = pos*voxel_tree.mask_block_dim*voxel_tree.voxel_world_size
                hit += vector3(x,y,z)*voxel_tree.voxel-world_size
                t = (hit - ray.s).mag()
                return coll( True, self, t )

            #increase along ray direction and then find the direction that
            #it moved out of this mask block first
            new_dp = dp + d
            out_of_bounds = (new_dp - mask_dim).component_div( d )
            m = max( enumerate( out_of_bounds.raw ), key = lambda t: t.__getitem__(1) )

            #position dp at the edge of the mask block
            t = ( voxel_tree.mask_block_dim - dp.raw[ m[0] ] ) / ld
            dp += d * t

            #increase pos which control with mask block we're looking at
            # then reset the submask-block index in that direction
            pos.modify( m[0], 1 )
            dp.modify( m[0], -voxel_tree.mask_block_dim )
                 
            
        #passed outside of voxel space, no collision
        return coll()


    def _create_mask( self, v ):
        """Returns: long representing bit mask of all the points the vector
        touches in crossing a mask block. v should be normalized"""
        
        mask = 0L
        start = vector3(0,0,0)
        if v.x < 0.0:   start.x = voxel_tree.mask_block_dim
        if v.y < 0.0:   start.y = voxel_tree.mask_block_dim
        if v.z < 0.0:   start.z = voxel_tree.mask_block_dim
        
        for i in range( 7 ):
            pos = start + (v * i);
            if pos.x < 4 and pos.x >=0 and pos.y < 4 and pos.y >=0 and pos.z < 4 and pos.z >= 0:
                shift = pos.x + pos.y * voxel_tree.mask_block_dim + pos.z * voxel_tree.mask_block_dim_sq
                mask = mask | ( 1 << int(shift) )
                
        return mask

    def eccentricity( self, ray ):
        return -100000000000.0

    def create_sphere( self, rel_pos, radius, mat ):

        self.m = mat
        
        rel_pos /= voxel_tree.voxel_world_size
        radius /= voxel_tree.voxel_world_size
        radius_sq = radius * radius
        
        for x in range( int(self.dim.x * voxel_tree.mask_block_dim) ):
            for y in range( int(self.dim.y * voxel_tree.mask_block_dim) ):
                for z in range( int(self.dim.z * voxel_tree.mask_block_dim) ):
                    print x,y,z
                    ptsq = ( (x-rel_pos.x)*(x-rel_pos.x) +
                             (y-rel_pos.y)*(y-rel_pos.y) +
                             (z-rel_pos.z)*(z-rel_pos.z) )
                    if ptsq < radius_sq:
                        mask = ( 1 << ( (x % voxel_tree.dim.x) +
                                        (y % voxel_tree.dim.y) * mask_block_dim
                                        (z % voxel_tree.dim.z) * mask_block_dim_sq ) )
                        pos = vector3(x,y,z) / voxel_tree.mask_block_dim
                        mask_pos = int( (pos.x / voxel_tree.pos.x +
                                         pos.y * voxel_tree.dim.x +
                                         pos.z * voxel_tree.dim.x * voxel_tree.dim.y ) )

                        self.mask[ mask_pos ] |= mask
                        
            
            
