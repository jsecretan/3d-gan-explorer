#!/usr/bin/env python
import os
import sys
import numpy as np
import tensorflow as tf
import skimage.measure as sk
import trimesh
import io
import random
from mesh_utility import decimate
from zipfile import ZipFile
import timeit

class GANGenerator:

    def __init__(self, trained_model_path):

        self.batch_size = 1
        self.z_size = 200

        self.weights = self.initialiseWeights()
        self.z_vector = tf.placeholder(shape=[self.batch_size,self.z_size],dtype=tf.float32) 
        self.net_g_test = self.generator(self.z_vector, self.batch_size, phase_train=True, reuse=False)

        self.sess = tf.Session()
        self.saver = tf.train.Saver()

        self.sess.run(tf.global_variables_initializer())
        self.saver.restore(self.sess, trained_model_path)


    def initialiseWeights(self):

        weights = {}

        xavier_init = tf.contrib.layers.xavier_initializer()

        weights['wg1'] = tf.get_variable("wg1", shape=[4, 4, 4, 512, 200], initializer=xavier_init)
        weights['wg2'] = tf.get_variable("wg2", shape=[4, 4, 4, 256, 512], initializer=xavier_init)
        weights['wg3'] = tf.get_variable("wg3", shape=[4, 4, 4, 128, 256], initializer=xavier_init)
        weights['wg4'] = tf.get_variable("wg4", shape=[4, 4, 4, 64, 128], initializer=xavier_init)
        weights['wg5'] = tf.get_variable("wg5", shape=[4, 4, 4, 1, 64], initializer=xavier_init)    

        weights['wd1'] = tf.get_variable("wd1", shape=[4, 4, 4, 1, 64], initializer=xavier_init)
        weights['wd2'] = tf.get_variable("wd2", shape=[4, 4, 4, 64, 128], initializer=xavier_init)
        weights['wd3'] = tf.get_variable("wd3", shape=[4, 4, 4, 128, 256], initializer=xavier_init)
        weights['wd4'] = tf.get_variable("wd4", shape=[4, 4, 4, 256, 512], initializer=xavier_init)    
        weights['wd5'] = tf.get_variable("wd5", shape=[4, 4, 4, 512, 1], initializer=xavier_init)    

        return weights


    def generator(self, z, batch_size, phase_train=True, reuse=False):

        strides    = [1,2,2,2,1]

        with tf.variable_scope("gen", reuse=reuse):
            z = tf.reshape(z, (batch_size, 1, 1, 1, self.z_size))
            g_1 = tf.nn.conv3d_transpose(z, self.weights['wg1'], (batch_size,4,4,4,512), strides=[1,1,1,1,1], padding="VALID")
            g_1 = tf.contrib.layers.batch_norm(g_1, is_training=phase_train)
            g_1 = tf.nn.relu(g_1)

            g_2 = tf.nn.conv3d_transpose(g_1, self.weights['wg2'], (batch_size,8,8,8,256), strides=strides, padding="SAME")
            g_2 = tf.contrib.layers.batch_norm(g_2, is_training=phase_train)
            g_2 = tf.nn.relu(g_2)

            g_3 = tf.nn.conv3d_transpose(g_2, self.weights['wg3'], (batch_size,16,16,16,128), strides=strides, padding="SAME")
            g_3 = tf.contrib.layers.batch_norm(g_3, is_training=phase_train)
            g_3 = tf.nn.relu(g_3)

            g_4 = tf.nn.conv3d_transpose(g_3, self.weights['wg4'], (batch_size,32,32,32,64), strides=strides, padding="SAME")
            g_4 = tf.contrib.layers.batch_norm(g_4, is_training=phase_train)
            g_4 = tf.nn.relu(g_4)
            
            g_5 = tf.nn.conv3d_transpose(g_4, self.weights['wg5'], (batch_size,64,64,64,1), strides=strides, padding="SAME")
            # g_5 = tf.nn.sigmoid(g_5)
            g_5 = tf.nn.tanh(g_5)

        return g_5


    def runGAN(self, object_space_value):

        z_sample = np.random.normal(0, object_space_value, size=[self.batch_size, self.z_size]).astype(np.float32)
        g_objects = self.sess.run(self.net_g_test,feed_dict={self.z_vector:z_sample})
        id_ch = np.random.randint(0, self.batch_size, 4)
        voxels = np.squeeze(g_objects[0]>0.5)
        vertices, faces, normals, values = sk.marching_cubes_lewiner(voxels, level=0.5)

        return vertices, faces, normals, values


    def generate_object(self, object_space, extension):
        vertices, faces, normals, values = self.runGAN(object_space)
     
        mesh = trimesh.base.Trimesh(vertices = vertices, faces = faces)

        # Remove artifacts by getting the largest component
        components = mesh.split()

        # TODO, there should be a way of making this more efficient
        largest_component = components[0]

        most_vertices = len(largest_component.vertices)
        for component in components:
            if len(component.vertices) > most_vertices:
                largest_component = component
                most_vertices = len(component.vertices)

        largest_component.vertices -= largest_component.centroid
        largest_component.vertices /= 10.0

        trimesh.repair.fill_holes(largest_component)
        trimesh.smoothing.filter_taubin(largest_component,iterations=10)

        reduced_mesh = decimate(largest_component)

        if extension == "stl":
            return trimesh.exchange.stl.export_stl_ascii(reduced_mesh)
        else:
            return trimesh.exchange.wavefront.export_wavefront(reduced_mesh)


#     def generate_multiple_objects(self, object_space):
#         z_sample = np.random.normal(0, object_space, size=[self.batch_size, self.z_size]).astype(np.float32)
#         g_objects = self.sess.run(self.net_g_test,feed_dict={self.z_vector:z_sample})
#         total_mesh_data_size = 0
# #        buff = io.BytesIO()
# #        zip = ZipFile(buff, mode='w')
#         for i in range(self.batch_size):
#             voxels = np.squeeze(g_objects[i]>0.5)
#             vertices, faces, normals, values = sk.marching_cubes_lewiner(voxels, level=0.5)
            
#             mesh = trimesh.base.Trimesh(vertices = vertices, faces = faces)

#             # Remove artifacts by getting the largest component
#             components = mesh.split()

#             # TODO, there should be a way of making this more efficient
#             largest_component = components[0]

#             most_vertices = len(largest_component.vertices)
#             for component in components:
#                 if len(component.vertices) > most_vertices:
#                     largest_component = component
#                     most_vertices = len(component.vertices)

#             largest_component.vertices -= largest_component.centroid
#             largest_component.vertices /= 10.0

#             trimesh.repair.fill_holes(largest_component)
#             trimesh.smoothing.filter_taubin(largest_component,iterations=10)

#             reduced_mesh = decimate(largest_component)

# #            zip.writestr(str(i)+".obj",trimesh.exchange.wavefront.export_wavefront(reduced_mesh))


#             with open(str(i)+".obj", "w") as file:
#                 #mesh_data = trimesh.exchange.wavefront.export_wavefront(largest_component)
#                 mesh_data = trimesh.exchange.wavefront.export_wavefront(reduced_mesh)
#                 total_mesh_data_size += len(mesh_data)
#                 file.write(mesh_data)

#         #print("Object size is %f" % (total_mesh_data_size/self.batch_size))
# #        zip.close()
# #        return buff.getvalue()


# if __name__ == "__main__":
#     g = GANGenerator("biasfree_998.cptk")
#     def run_request_test():
#         g.generate_multiple_objects(0.5123)
    
#     total_time = timeit.timeit(run_request_test, number=1)

#     print("On average objects took %f to compute" % (total_time/g.batch_size))



